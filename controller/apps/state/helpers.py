from collections import OrderedDict
from django.db.models import Count

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


REPORT_NODE_STATES = {
    'online': ['production'],
    'unknown': ['unknown', 'nodata'],
    'offline': ['debug', 'safe', 'offline', 'crashed', 'failure'],
}

REPORT_SLIVER_STATES = (
    ('sliver_registered', 'registered'),
    ('sliver_started', 'started'),
    ('sliver_deployed', 'deployed'),
)

def get_state_report(state):
    for key, values in REPORT_NODE_STATES.items():
        if state in values:
            return key
    raise ValueError("Uknown node state value: '%s'" % state)

def get_report_data():
    """ Fetch testbed data to generate the report """
    from nodes.models import Node
    from slices.models import Sliver, Slice
    from users.models import Group
    # get data from the database
    # multiple annotations: http://stackoverflow.com/a/1266787/1538221
    qs_groups = Group.objects.all().order_by('name').annotate(Count('slices', distinct=True), Count('nodes', distinct=True), Count('slices__slivers', distinct=True))
    nodes = qs_groups.values('id', 'nodes__state_set__value').annotate(Count('nodes'))
    slivers = qs_groups.values('id', 'slices__slivers__state_set__value').annotate(Count('slices__slivers'))

    # normalice and prepare data to the template
    groups = OrderedDict()
    for item in qs_groups.values('id', 'name', 'nodes__count', 'slices__count', 'slices__slivers__count'):
        id = item.get('id')
        groups[id] = item
    del(item)

    for node in nodes: # aggregate in aggrupated states
        group = groups.get(node.get('id'))
        state = node.get('nodes__state_set__value')
        if state is None:
            continue
        state_report = "nodes__count__%s" % get_state_report(state)
        nodes_count = node.get('nodes__count')
        if state_report in group.keys():
            group[state_report] += nodes_count
        else: 
            group[state_report] = nodes_count
    del(node, nodes)
        
    for slv in slivers:
        group = groups.get(slv.get('id'))
        state = "slices__slivers__count__%s" % slv.get('slices__slivers__state_set__value')
        group[state]  = slv.get('slices__slivers__count')
    del(slv, slivers)

    # calculate TOTAL
    online = REPORT_NODE_STATES['online']
    offline = REPORT_NODE_STATES['offline']
    unknown =  REPORT_NODE_STATES['unknown']
    total = {
        'nodes_online': Node.objects.filter(state_set__value__in=online).count(),
        'nodes_offline': Node.objects.filter(state_set__value__in=offline).count(),
        'nodes_unknown': Node.objects.filter(state_set__value__in=unknown).count(),
        'nodes_total':  Node.objects.count(),
        'slices_total': Slice.objects.count(),
        'slivers_registered': Sliver.objects.filter(state_set__value='registered').count(),
        'slivers_deployed': Sliver.objects.filter(state_set__value='deployed').count(),
        'slivers_started': Sliver.objects.filter(state_set__value='started').count(),
        'slivers_total': Sliver.objects.count(),
    }
    
    return groups, total
