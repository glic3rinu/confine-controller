from __future__ import absolute_import

from api.renderers import ProfileJSONRenderer


class UserProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v0/user'


class GroupProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v0/group'
