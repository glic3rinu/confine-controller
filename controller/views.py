from rest_framework.views import APIView
from rest_framework.response import Response

BASE_API_URL = '/confine'

class Base(APIView):
    def get(self, request, format=None):
        print dir(request._request)
        print request._request
        testbed_params = {
            "mgmt_ipv6_prefix": "2001:db8:cafe::/48",
            "priv_ipv4_prefix_dflt": "192.168.157.0/24",
            "sliver_mac_prefix_dflt": "0x06ab", }

        output = {"testbed_params": testbed_params,
                  "server_href": "%s/server" % BASE_API_URL,
                  "nodes_href": "%s/nodes/" % BASE_API_URL,
                  "slices_href": "%s/slices/" % BASE_API_URL,
                  "slivers_href": "%s/slivers/" % BASE_API_URL,
                  "users_href": "%s/users/" % BASE_API_URL,
                  "gateways_href": "%s/gateways/" % BASE_API_URL,
                  "hosts_href": "%s/hosts/" % BASE_API_URL,
                  "templates_href": "%s/templates/" % BASE_API_URL,
                  "islands_href": "%s/islands/"% BASE_API_URL,}

        return Response(output)

