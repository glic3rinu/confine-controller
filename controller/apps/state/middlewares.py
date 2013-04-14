from .models import NodeState


class NodePullHeartBeat(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'nodes.api' == view_func.__module__:
            from mgmtnetworks.utils import reverse
            client = reverse(request.META['REMOTE_ADDR'])
            if client and str(client._meta) == 'nodes.node':
                NodeState.register_heartbeat(client)
