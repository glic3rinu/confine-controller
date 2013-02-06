from __future__ import absolute_import

from api import ApiRoot
from controller.utils import is_installed
from nodes import settings as nodes_settings


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
    def get(self, *args, **kwargs):
        response = super(Base, self).get(*args, **kwargs)
        testbed_params = {
            "priv_ipv4_prefix_dflt": nodes_settings.NODES_PRIV_IPV4_PREFIX_DFLT,
            "sliver_mac_prefix_dflt": nodes_settings.NODES_SLIVER_MAC_PREFIX_DFLT, }
        
        if is_installed('mgmtnetworks.tinc'):
            from mgmtnetworks.tinc.settings import TINC_MGMT_IPV6_PREFIX
            testbed_params.update({"mgmt_ipv6_prefix": TINC_MGMT_IPV6_PREFIX})
        response.data.update({"testbed_params": testbed_params})
        return response
