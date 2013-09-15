from .models import State


class NodePullHeartBeat(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.__module__ in ('nodes.api', 'slivers.api'):
            from mgmtnetworks.utils import reverse
            client = reverse(request.META['REMOTE_ADDR'])
            if client: print str(client._meta)
            if client and str(client._meta) in ('nodes.node', 'slices.sliver'):
                print client
                State.register_heartbeat(client)
