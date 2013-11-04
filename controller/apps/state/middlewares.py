class NodePullHeartBeat(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.func_name in ('NodeDetail', 'SliverDetail'):
            from controller.core.exceptions import InvalidMgmtAddress
            from nodes.utils import get_mgmt_backend_class
            mgmt_backend = get_mgmt_backend_class()
            META = request.META
            remote_addr = META.get('HTTP_X_REAL_IP', META['REMOTE_ADDR'])
            try:
                client = mgmt_backend.reverse(remote_addr)
            except InvalidMgmtAddress:
                return
            from nodes.models import Node
            if isinstance(client, Node):
                from .models import State
                if view_func.func_name == 'NodeDetail':
                    State.register_heartbeat(client)
                elif view_func.func_name == 'SliverDetail':
                    from slices.models import Sliver
                    try:
                        sliver = Sliver.objects.get(pk=view_kwargs.get('pk'))
                    except Sliver.DoesNotExist:
                        pass
                    else:
                        State.register_heartbeat(sliver)
