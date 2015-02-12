from __future__ import absolute_import

from api.renderers import ProfileJSONRenderer


class IslandProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v1/island'


class NodeProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v1/node'


class ServerProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v1/server'
