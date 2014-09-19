from __future__ import absolute_import

from django.utils.safestring import mark_safe
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.reverse import reverse

from api import ApiRoot
from controller import settings
from controller.models import Testbed
from controller.serializers import TestbedSerializer
from controller.renderers import BaseProfileRenderer


class Base(ApiRoot):
    """ 
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/base"`](
        http://wiki.confine-project.eu/arch:rest-api#base_at_registry)
    
    This resource is located at the base URI of the registry API. It
    describes testbed-wide parameters and provides the API URIs to
    navigate to other resources in the testbed.
    
    Note that you can also explore the API from the command line, for
    instance using the curl command-line tool.
    
    For example: `curl -X GET %(url)s -H "Accept: application/json;
        indent=4"`
    """
    renderer_classes = [BaseProfileRenderer, BrowsableAPIRenderer]
    
    def get_object(self):
        return Testbed.objects.get()
    
    def get(self, request, *args, **kwargs):
        response = super(Base, self).get(request, *args, **kwargs)
        
        # testbed_params + testbed_resources
        testbed = self.get_object()
        serializer = TestbedSerializer(testbed)
        response.data.update(serializer.data)
        
        confine_params = {
            "debug_ipv6_prefix": settings.DEBUG_IPV6_PREFIX,
            "priv_ipv6_prefix": settings.PRIV_IPV6_PREFIX
        }
        response.data.update({
            "uri": reverse('base', request=request),
            "confine_params": confine_params })
        return response
    
    def get_description(self, html=False):
        """ fills docstring %(site)s """
        description = super(Base, self).get_description(html=html)
        description = description % {'url': reverse('base', request=self.request)}
        if html:
            description = mark_safe(description)
        return description

