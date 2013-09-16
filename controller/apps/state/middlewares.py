class NodePullHeartBeat(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.func_name in ('NodeDetail', 'SliverDetail'):
            from mgmtnetworks.utils import reverse
            client = reverse(request.META['REMOTE_ADDR'])
            pk = view_kwargs.get('pk')
            if client:
                from .models import State
                if view_func.func_name == 'NodeDetail':
                    State.register_heartbeat(client)
                elif view_func.func_name == 'SliverDetail':
                    from slices.models import Sliver
                    sliver = Sliver.objects.get(pk=view_kwargs.get('pk'))
                    State.register_heartbeat(sliver)
