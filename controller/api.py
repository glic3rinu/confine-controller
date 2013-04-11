from __future__ import absolute_import

from rest_framework.reverse import reverse

from api import ApiRoot
from controller import settings
from controller.utils import is_installed


class Base(ApiRoot):
    """ 
    **Media type:** [`application/vnd.confine.server.Base.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#base_at_server)
    
    This resource is located at the base URI of the server API. It 
    describes testbed-wide parameters and provides the API URIs to 
    navigate to other resources in the testbed.
    
    Note that you can also explore the API from the command line, for 
    instance using the curl command-line tool.
    
    For example: `curl -X GET https://controller.confine-project.eu/api/
    -H "Accept: application/json; indent=4"`
    """
    def get(self, request, *args, **kwargs):
        response = super(Base, self).get(request, *args, **kwargs)
        
        testbed_params = {
            "priv_ipv4_prefix_dflt": settings.PRIV_IPV4_PREFIX_DFLT,
            "sliver_mac_prefix_dflt": settings.SLIVER_MAC_PREFIX_DFLT,
            "mgmt_ipv6_prefix": settings.MGMT_IPV6_PREFIX,
        }
        confine_params = {
            "debug_ipv6_prefix": settings.DEBUG_IPV6_PREFIX,
            "priv_ipv6_prefix": settings.PRIV_IPV6_PREFIX
        }
        response.data.update({
            "uri": reverse('base', request=request),
            "testbed_params": testbed_params,
            "confine_params": confine_params })
        return response



