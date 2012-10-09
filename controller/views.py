from nodes import settings as nodes_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

#TODO: make this pluggable !!! api.register() or something clean

class Base(APIView):
    """ 
        This resource is located at the base URI of the server API. It describes 
        testbed-wide parameters and provides the API URIs to navigate to other 
        resources in the testbed.
    """
    
    def get(self, request, format=None):
        testbed_params = {
            "mgmt_ipv6_prefix": nodes_settings.MGMT_IPV6_PREFIX,
            "priv_ipv4_prefix_dflt": nodes_settings.PRIV_IPV4_PREFIX_DFLT,
            "sliver_mac_prefix_dflt": nodes_settings.SLIVER_MAC_PREFIX_DFLT, }

        output = {"testbed_params": testbed_params,
#                  "server_href": "%s/server" % BASE_API_URL,
                  "nodes_href": reverse('node-list', args=[], request=request),
#                  "slices_href": "%s/slices/" % BASE_API_URL,
#                  "slivers_href": "%s/slivers/" % BASE_API_URL,
                  "users_href": reverse('user-list', args=[], request=request),
#                  "gateways_href": "%s/gateways/" % BASE_API_URL,
#                  "hosts_href": "%s/hosts/" % BASE_API_URL,
#                  "templates_href": "%s/templates/" % BASE_API_URL,
#                  "islands_href": "%s/islands/"% BASE_API_URL,
        }

        return Response(output)

