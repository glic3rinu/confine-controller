from collections import OrderedDict

from nodes.models import Node
from slices.models import Slice
from state.models import State
from users.models import Group

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


def get_report_data():
    REPORT_STATES = {
        'online': [Node.PRODUCTION],
        'offline': [State.OFFLINE, State.CRASHED, Node.DEBUG, Node.SAFE, State.FAILURE, 
                    'fail_alloc', 'fail_deploy', 'fail_start'],
        'registered': [Slice.REGISTER],
        'deployed': [Slice.DEPLOY],
        'started': [Slice.START],
        'unknown': [State.UNKNOWN, State.NODATA],
    }
    
    totals = {}
    groups = OrderedDict()
    base_query = State.objects.values_list('value', flat=True)
    for group in Group.objects.all().order_by('name'):
        groups[group] = {}
        queryes = {
           'nodes': base_query.filter(node__group=group, content_type__model='node'),
           'slivers': base_query.filter(sliver__slice__group=group, content_type__model='sliver'),
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
                        groups[group][relation].setdefault(report, 0)
                        totals[relation].setdefault(report, 0)
                        totals[relation][report] += 1
                        total += 1
                        break
            groups[group][relation]['total'] = total
            totals[relation].setdefault('total', 0)
            totals[relation]['total'] += total
    return { 'groups': groups, 'totals': totals }
