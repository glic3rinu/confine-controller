from collections import OrderedDict
from django.contrib.contenttypes.models import ContentType
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

# Using RAW SQL until this bug is fixed (annotate not filtering per content_type)
# https://code.djangoproject.com/ticket/10461
# REPLACE IT when nodes.query == RAW_SQL_NODES and slivers.query == RAW_SQL_SLIVERS
RAW_SQL_NODES = 'SELECT "users_group"."id", "state_state"."value", COUNT("nodes_node"."id") AS "nodes__count" \
    FROM "users_group" \
    LEFT OUTER JOIN "nodes_node" ON ("users_group"."id" = "nodes_node"."group_id") \
    LEFT OUTER JOIN "state_state" ON ("nodes_node"."id" = "state_state"."object_id" AND "state_state"."content_type_id" = %s) \
    GROUP BY "users_group"."id", "state_state"."value" \
    ORDER BY "users_group"."name" ASC'
    #nodes = qs_base.values('id', 'nodes__state_set__value').annotate(Count('nodes'))

RAW_SQL_SLIVERS = 'SELECT "users_group"."id", "state_state"."value", COUNT("slices_sliver"."id") AS "slices__slivers__count" \
    FROM "users_group" \
    LEFT OUTER JOIN "slices_slice" ON ("users_group"."id" = "slices_slice"."group_id") \
    LEFT OUTER JOIN "slices_sliver" ON ("slices_slice"."id" = "slices_sliver"."slice_id") \
    LEFT OUTER JOIN "state_state" ON ("slices_sliver"."id" = "state_state"."object_id" AND "state_state"."content_type_id" = %s) \
    GROUP BY "users_group"."id", "state_state"."value", "users_group"."name" \
    ORDER BY "users_group"."name" ASC'
    #slivers = qs_base.values('id', 'slices__slivers__state_set__value').annotate(Count('slices__slivers'))

def get_report_data():
    """ Fetch testbed data to generate the report """
    from nodes.models import Node
    from slices.models import Sliver, Slice
    from users.models import Group
    # get data from the database
    # multiple annotations: http://stackoverflow.com/a/1266787/1538221
    qs_base = Group.objects.all().order_by('name')
    qs_groups = qs_base.annotate(
                    Count('slices', distinct=True),
                    Count('nodes', distinct=True),
                    Count('slices__slivers', distinct=True)
                )
    ct_node = ContentType.objects.get(model='node')
    nodes = Group.objects.raw(RAW_SQL_NODES, [ct_node.id])
    ct_sliver = ContentType.objects.get(model='sliver')
    slivers = Group.objects.raw(RAW_SQL_SLIVERS, [ct_sliver.id])

    # normalice and prepare data to the template
    groups = OrderedDict()
    for item in qs_groups.values('id', 'name', 'nodes__count', 'slices__count', 'slices__slivers__count'):
        id = item.get('id')
        groups[id] = item
    del(item)

    for node in nodes: # aggregate in aggrupated states
        group = groups.get(node.id)
        state = node.value
        if state is None or state == '':
            continue
        state_report = "nodes__count__%s" % get_state_report(state)
        nodes_count = node.nodes__count
        if state_report in group.keys():
            group[state_report] += nodes_count
        else: 
            group[state_report] = nodes_count
    del(node, nodes)
        
    for slv in slivers:
        group = groups.get(slv.id)
        state = "slices__slivers__count__%s" % slv.value
        group[state]  = slv.slices__slivers__count
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
