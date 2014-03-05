import datetime
from collections import OrderedDict
from dateutil.relativedelta import relativedelta

from django.utils import timezone

from nodes.models import Node
from slices.models import Slice, Sliver
from users.models import Group

from .models import State, NodeSoftwareVersion
from .settings import STATE_NODE_SOFT_VERSION_URL, STATE_NODE_SOFT_VERSION_NAME


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
    versions = NodeSoftwareVersion.objects.distinct('value').extra(
        select={'date': "SUBSTRING(value from '-r........')"}).values('date', 'value')
    versions = sorted(versions, key=lambda k: k['date'], reverse=True)[:4]
    
    totals = OrderedDict()
    groups = OrderedDict()
    qs_groups = Group.objects.filter(id__in=Node.objects.values_list('group',
        flat=True).distinct('group'))
    for group in qs_groups:
        nodes = Node.objects.filter(group=group)
        sw_data = []
        version_count = 0
        for version in versions:
            count = nodes.filter(soft_version__value=version['value']).count()
            name = STATE_NODE_SOFT_VERSION_NAME(version['value'])
            url = STATE_NODE_SOFT_VERSION_URL(version['value'])
            sw_data.append({
                'name': name,
                'url': url,
                'count': count
            })
            totals.setdefault(name, {'url': url, 'count':0})
            totals[name]['count'] += count
            version_count += count
        
        # aggregate nodes without firmware version data
        nodata_count = nodes.filter(soft_version__isnull=True).count()
        sw_data.append({
            'name': 'N/A',
            'count': nodata_count
        })

        # aggregate old firmware versions
        others_count = nodes.count() - (version_count + nodata_count)
        sw_data.append({
            'name': 'Other',
            'count': others_count
        })
        
        # store aggregated data
        groups[group] = sw_data
        totals.setdefault('N/A', {'title': 'No data', 'count':0})
        totals.setdefault('Other', {'title': 'Old firmware versions', 'count':0})
        totals['N/A']['count'] += nodata_count
        totals['Other']['count'] += others_count
    
    return { 'groups': groups, 'totals': totals }
