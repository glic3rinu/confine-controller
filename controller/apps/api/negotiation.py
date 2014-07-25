from rest_framework.exceptions import NotAcceptable
from rest_framework.negotiation import DefaultContentNegotiation

class ProfileContentNegotiation(DefaultContentNegotiation):
     def select_renderer(self, request, renderers, format_suffix=None):
        try:
            return super(ProfileContentNegotiation, self).select_renderer(request,
                renderers, format_suffix=format_suffix)
        except NotAcceptable:
            # ProfileRenderer acts as application/json renderer
            if "application/json" in self.get_accept_list(request):
                return renderers[0], renderers[0].media_type
            raise
