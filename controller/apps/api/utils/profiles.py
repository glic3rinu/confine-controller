class _Profile(object):
    CONFINE_SCHEMA_URI = "http://confine-project.eu/schema/"
    
    api = None
    version = None
    resource = None
    
    def __init__(self, profile_uri):
        # profile="http://confine-project.eu/schema/<API>[/<API_VERSION>]/<RESOURCE>"
        # <API>: [registry|node|controller]
        # <API_VERSION>: v[0-9]+
        # <RESOURCE>: resource_name[-list]
        if profile_uri is None:
            return
        
        if not profile_uri.startswith(_Profile.CONFINE_SCHEMA_URI):
            raise ValueError("Invalid literal for profile URI: '%s'" % profile_uri)
        
        profile = profile_uri.replace(_Profile.CONFINE_SCHEMA_URI, "").split('/')
        if len(profile) == 2:
            self.api, self.resource = profile
        elif len(profile) == 3:
            self.api, self.version, self.resource = profile
        else:
            raise ValueError("Invalid literal for profile URI: '%s'" % profile_uri)


def profile_matches(first, other):
    first = _Profile(first)
    other = _Profile(other)
    
    if first.api and other.api and first.api != other.api:
        return False
    
    if first.version and other.version and first.version != other.version:
        return False

    if first.resource and other.resource and first.resource != other.resource:
        return False
    
    return True
