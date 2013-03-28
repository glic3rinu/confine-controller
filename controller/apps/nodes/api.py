from __future__ import absolute_import

from django.http import Http404

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import Node, Server
from .serializers import ServerSerializer, NodeSerializer


from django.views.generic import View

class ApiFunction(View):
    url_prefix = 'ctl/'


#def action_to_api_function(action, model):
#    """ Converts modeladmin action to api view function """
#    modeladmin = get_modeladmin(model)
#    def api_function(request, object_id, modeladmin=modeladmin, action=action):
#        queryset = model.objects.filter(pk=object_id)
#        response = action(modeladmin, request, queryset)
#        return response
#    return api_function


class RebootFunction(ApiFunction):
    def post(self, request, *args, **kwargs):
        action = action_to_api_function(request_cert, Node)
        response = action(request, *args, **kwargs)
        return super(RebootAction, self).post(request, *args, **kwargs)



class RequestCertFunction(ApiFunction):
    def post(self, request, *args, **kwargs):
        pass


class NodeList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """ 
    **Media type:** [`application/vnd.confine.server.Node.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#node_at_server)
    
    This resource lists the [nodes](http://wiki.confine-project.eu/arch:rest-
    api?&#node_at_server) available in the testbed and provides API URIs to 
    navigate to them.
    """
    model = Node
    serializer_class = NodeSerializer
    filter_fields = ('arch', 'set_state', 'group', 'group__name')
#    functions = [RebootFunction, RequestCertFunction]



class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Node.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#node_at_server)
    
    This resource describes a node in the testbed as well as listing the 
    [slivers](http://wiki.confine-project.eu/arch:rest-api?&#sliver_at_server)
    intended to run on it with API URIs to navigate to them.
    """
    model = Node
    serializer_class = NodeSerializer


class ServerDetail(generics.RetrieveUpdateDestroyAPIView):
    """ 
    **Media type:** [`application/vnd.confine.server.Server.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#server_at_server)
    
    This resource describes the testbed server (controller).
    """
    model = Server
    serializer_class = ServerSerializer
    
    def get_object(self, *args, **kwargs):
        try:
            return Server.objects.get()
        except Server.DoesNotExist:
            raise Http404


api.register(NodeList, NodeDetail)
api.register(ServerDetail, ServerDetail)
