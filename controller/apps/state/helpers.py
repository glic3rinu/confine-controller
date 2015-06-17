import datetime
import json
import requests
import ssl

from collections import OrderedDict
from contextlib import closing
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from controller.utils.ssl import SSLAdapter

from nodes.models import Node
from pki import ca
from slices.models import Slice, Sliver
from users.models import Group

from .settings import (STATE_FETCH_TIMEOUT_CONNECT, STATE_FETCH_TIMEOUT_READ,
    STATE_NODE_SOFT_VERSION_URL, STATE_NODE_SOFT_VERSION_NAME)


def break_headers(header):
    header = header.replace(', <', ',\n                 <')
    return header.replace(' (', '\n                  (')


def break_lines(text, every=150):
    result = []
    for line in text.split('\n'):
        every = text.find('\\n')
        if every != -1:
            distance = line.find(':') + 3
            line = line.replace('\\n', '\n' + ' '*distance)
        result.append(line)
    return '\n'.join(result)


def fetch_state(obj):
    """
    Fetch object state via Node API.

    Node API certificate will be verified against controller CA
    (if any), although verification fails, state will be retrieved
    but marked as not trusted.
    """
    # Use HTTP Etag to allow 304 Not Modified to be returned
    try:
        etag = json.loads(obj.state.metadata)['headers']['etag']
    except (ValueError, KeyError):
        headers = {}
    else:
        headers = {'If-None-Match': etag}
    
    # CNS only supports TLSv1 but requests use whatever
    # version is default in the underlying library so we
    # need to use a HttpAdater to ensure compatibility
    session = requests.Session()
    session.mount('https://', SSLAdapter(ssl_version=ssl.PROTOCOL_TLSv1))
    session.verify = ca.cert_path
    obj_state_url = obj.state.get_url()
    
    # set timeout to avoid waiting until connection expires
    # using tuple (connect, read) timeout requires requests 2.4+
    timeout = (STATE_FETCH_TIMEOUT_CONNECT, STATE_FETCH_TIMEOUT_READ)
    
    try:
        response = session.get(obj_state_url, headers=headers, timeout=timeout)
        response.headers['ssl_verified'] = obj_state_url.startswith('https')
    except requests.exceptions.SSLError:
        session.verify = False
        response = session.get(obj_state_url, headers=headers, timeout=timeout)
        response.headers['ssl_verified'] = False
        ## TODO(santiago) Parse response because cames from an untrusted node ##
        #with closing(session.get(obj_state_url, headers=headers, stream=True, timeout=5)) as response:
        #    response.headers['ssl_verified'] = False
        #    # Limit response size
        #    if response.headers.get('content-length') is None:
        #        raise RuntimeError('Unknown content-length.')
        #    if int(response.headers['content-length']) > 32768: # 32 KiB
        #        raise RuntimeError('Node response is too long (max content-length exceded).')
        #    # Handle malformed or not JSON response
        #    # FIXME: response can be empty '', json convertion fails! (#629)
        #    try:
        #        response.json()
        #    except ValueError:
        #        raise RuntimeError('Malformed JSON in node response.')
    return response


def get_changes_data(state):
    from .admin import STATES_COLORS
    
    history = state.history
    now = timezone.now()
    delta = relativedelta(months=+1)
    year = now.year+1 if now.month == 12 else now.year
    final = datetime.datetime(year=year, month=(now.month%12)+1, day=1, tzinfo=timezone.utc)
    monthly = OrderedDict()
    distinct_states = set()
    # Get monthly changes
    for m in range(1, 13):
        initial = final-delta
        changes = history.filter(start__lt=final, end__gt=initial)
        if not changes:
            break
        states = {}
        for value, start, end in changes.values_list('value', 'start', 'end'):
            distinct_states = distinct_states.union(set((value,)))
            if start < initial:
                start = initial
            if end > final:
                end = final
            duration = int((end-start).total_seconds())
            states[value] = states.get(value, 0)+duration
        monthly[initial.strftime("%B")] = states
        final = initial
    # Fill missing states
    data = {}
    for month, duration in monthly.iteritems():
        current_states = set()
        for state in duration:
            data.setdefault(state, []).insert(0, duration[state])
            current_states = current_states.union(set((state,)))
        for missing in distinct_states-current_states:
            data.setdefault(missing, []).insert(0, 0)
    # Construct final data structure
    series = []
    months = monthly.keys()
    months.reverse()
    for state in data:
        series.append({
            'name': state,
            'data': data[state],
            'color': STATES_COLORS.get(state, None)
        })
    return { 'categories': months, 'series': series }


def get_report_data():
    from .models import State
    REPORT_STATES = {
        'online': [Node.PRODUCTION],
        'offline': [State.OFFLINE, State.CRASHED, Node.DEBUG, Node.SAFE, State.FAILURE, 
                    'fail_allocate', 'fail_deploy', 'fail_start'],
        'registered': 'registered',
        'deployed': 'deployed',
        'started': 'started',
        'unknown': [State.UNKNOWN, State.NODATA],
    }
    
    totals = {}
    groups = OrderedDict()
    for group in Group.objects.all().order_by('name'):
        groups[group] = {}
        queryes = {
           'nodes': Node.objects.filter(group=group).values_list('state_set__value', flat=True),
           'slivers': Sliver.objects.filter(slice__group=group).values_list('state_set__value', flat=True),
           'slices': Slice.objects.filter(group=group).values_list('set_state', flat=True),
        }
        for relation, query in queryes.iteritems():
            total = 0
            groups[group][relation] = {}
            totals.setdefault(relation, {})
            for current in query:
                for report, states in REPORT_STATES.iteritems():
                    if current in states:
                        groups[group][relation].setdefault(report, 0)
                        groups[group][relation][report] += 1
                        totals[relation].setdefault(report, 0)
                        totals[relation][report] += 1
                        total += 1
                        break
            groups[group][relation]['total'] = total
            totals[relation].setdefault('total', 0)
            totals[relation]['total'] += total
    return { 'groups': groups, 'totals': totals }


def get_node_version_data():
    """ Get stats about software version of nodes by groups
        NOTE: only the most recent, old versions will be grouped.
    """
    from .models import NodeSoftwareVersion
    master_versions = NodeSoftwareVersion.objects.ordered_versions('master')
    testing_versions = NodeSoftwareVersion.objects.ordered_versions('testing')
    versions = master_versions[:2] + testing_versions
    versions = sorted(versions[:4], key=lambda v: v.version['date'], reverse=True)
    
    totals = OrderedDict()
    groups = OrderedDict()
    qs_groups = Group.objects.filter(id__in=Node.objects.values_list('group',
        flat=True).distinct('group'))
    for group in qs_groups:
        nodes = Node.objects.filter(group=group)
        sw_data = []
        version_count = 0
        for version in versions:
            count = nodes.filter(soft_version__value=version.value).count()
            sw_data.append({
                'name': version.name,
                'url': version.url,
                'count': count
            })
            totals.setdefault(version.name, {'url': version.url, 'count':0})
            totals[version.name]['count'] += count
            version_count += count
        
        # aggregate nodes without firmware version data
        nodata_count = nodes.filter(soft_version__isnull=True).count()
        sw_data.append({
            'name': 'N/A',
            'count': nodata_count
        })

        # aggregate other firmware versions
        others_count = nodes.count() - (version_count + nodata_count)
        sw_data.append({
            'name': 'Other',
            'count': others_count
        })
        
        # store aggregated data
        groups[group] = sw_data
        totals.setdefault('N/A', {'title': 'No data', 'count':0})
        totals.setdefault('Other', {'title': 'Other firmware versions', 'count': 0})
        totals['N/A']['count'] += nodata_count
        totals['Other']['count'] += others_count
    
    return { 'groups': groups, 'totals': totals }


def sizeof_fmt(num, unit=None):
    """
    Get human readable version of storage size.
    @num should be provided as Megabyte
    Based on http://stackoverflow.com/a/1094933/1538221
    """
    # handle non default explicit units
    if unit is not None and unit != 'MiB':
        return "%.f %s" % (num, unit)
    try:
        num = float(num)
    except (TypeError, ValueError):
        return num
    for i, unit in enumerate(['MiB','GiB']):
        if abs(num) < 1024.0:
            size_format = "%3.0f %s" if i == 0 else "%3.1f %s"
            return (size_format % (num, unit)).strip()
        num /= 1024.0
    return "%.f %s" % (num, 'TiB')


def extract_node_software_version(version):
    """
    Extract version data from Node API reported string. Schema:
    <branch_name>.<first7hex_revision><rYYYYmmDD.HHMM><pkg_version>
    
    @return dictionary with branch, rev, date, pkg keys.
    """
    raw, _, pkg = version.rpartition('-')
    raw, _, date = raw.rpartition('-')
    branch, _, rev = raw.rpartition('.')
    return {'branch': branch, 'rev': rev, 'date': date, 'pkg': pkg}


def extract_disk_available(statejs):
    # legacy disk info (node firmware < 2014-09-02)
    total = statejs.get('disk_avail')
    slv_dflt = statejs.get('disk_dflt_per_sliver')
    
    # standar disk info via resources management
    disk_resource = {}
    for resource in statejs.get('resources', {}):
        if resource.get('name') == 'disk':
            disk_resource = resource
            break
    return {
        'total': total or disk_resource.get('avail', 'N/A'),
        'slv_dflt': slv_dflt or disk_resource.get('dflt_req', 'N/A'),
        'unit': disk_resource.get('unit')
    }
