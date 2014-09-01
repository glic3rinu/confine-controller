from rest_framework.renderers import JSONRenderer


class ProfileJSONRenderer(JSONRenderer):
    """
    Update media type to include extra parameter 'profile'
    including the confine schema. e.g. while rendering a user
    'application/json; profile="http://confine-project.eu/schema/registry/v0/user"'
    """
    profile = None # should be defined by subclasses
    
    def __init__(self, *args, **kwargs):
        if self.profile:
            self.media_type = 'application/json; profile="%s"' % self.profile
        super(ProfileJSONRenderer, self).__init__(*args, **kwargs)


class ResourceListJSONRenderer(JSONRenderer):
    """Define media type to resources lists at registry."""
    media_type = 'application/json; profile="http://confine-project.eu/schema/registry/v0/resource-list"'
