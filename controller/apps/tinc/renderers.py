from __future__ import absolute_import

from api.renderers import ProfileJSONRenderer


class HostProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v0/host'
