from admin_tools.dashboard.modules import DashboardModule

from nodes.models import Node
from slices.models import Slice

class MyThingsDashboardModule(DashboardModule):
    """
    Controller dashboard module to provide an overview to
    the user of the nodes and slices of its groups.
    """
    title="My Things"
    template = "dashboard/modules/mythings.html"
    
    def init_with_context(self, context):
        user = context['request'].user
        
        # Get user slices
        slices = Slice.objects.filter(group__in=user.groups.all().values_list('pk', flat=True))
        context['slices'] = slices
        
        # Get user nodes
        nodes = {}
        nodes_states = ['offline', 'safe', 'production']
        for group in user.groups.all():
            nodes[group] = []
            qs_nodes = Node.objects.filter(group=group)
            for state in nodes_states:
                nodes[group].append(qs_nodes.filter(state_set__value=state).count())
        
        context['nodes_states'] = nodes_states
        context['user_nodes'] = nodes
        
        # initialize to calculate is_empty
        self.has_data = nodes or slices
    
    def is_empty(self):
        return not self.has_data
