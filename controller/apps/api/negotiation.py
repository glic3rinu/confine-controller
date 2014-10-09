from rest_framework.exceptions import NotAcceptable
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.utils.mediatypes import _MediaType, order_by_precedence

from .utils.profiles import _Profile, profile_matches


def media_type_matches(first, other):
    """Return true if this MediaType satisfies the given MediaType."""
    first = _MediaType(first)
    other = _MediaType(other)
    for key in first.params.keys():
        if key != 'profile' and other.params.get(key, None) != first.params.get(key, None):
            return False
    
    # handle specific profile parameter
    try:
        if not profile_matches(first.params.get('profile', None),
                               other.params.get('profile', None)):
            return False
    except ValueError:
        raise NotAcceptable("Invalid profile requested." )

    if (first.sub_type != '*' and other.sub_type != '*'  and
        other.sub_type != first.sub_type):
        return False

    if (first.main_type != '*' and other.main_type != '*' and
        other.main_type != first.main_type):
        return False

    return True


class ProfileContentNegotiation(DefaultContentNegotiation):
    """
    Override select_renderer to accept 'profile' parameter
    while keep matching as default and json renderers.
    https://github.com/tomchristie/django-rest-framework/blob/2.3.14/rest_framework/negotiation.py
    
    """
    def select_renderer(self, request, renderers, format_suffix=None):
        # Allow URL style format override.  eg. "?format=json
        format_query_param = self.settings.URL_FORMAT_OVERRIDE
        format = format_suffix or request.QUERY_PARAMS.get(format_query_param)
        
        if format:
            renderers = self.filter_renderers(renderers, format)
        
        accepts = self.get_accept_list(request)
        
        # Check the acceptable media types against each renderer,
        # attempting more specific media types first
        # NB. The inner loop here isn't as bad as it first looks :)
        #     Worst case is we're looping over len(accept_list) * len(self.renderers)
        for media_type_set in order_by_precedence(accepts):
            for renderer in renderers:
                for media_type in media_type_set:
                    if media_type_matches(renderer.media_type, media_type):
                        # Return the most specific media type as accepted.
                        if (_MediaType(renderer.media_type).precedence >=
                            _MediaType(media_type).precedence):
                            # Eg client requests '*/*'
                            # Accepted media type is 'application/json'
                            return renderer, renderer.media_type
                        else:
                            # Eg client requests 'application/json; indent=8'
                            # Accepted media type is 'application/json; indent=8'
                            return renderer, media_type
        
        raise NotAcceptable(available_renderers=renderers)
