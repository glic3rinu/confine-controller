from __future__ import absolute_import

from api.renderers import ProfileJSONRenderer


class BaseProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v0/base'
