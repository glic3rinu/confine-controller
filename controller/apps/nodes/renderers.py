from __future__ import absolute_import

from api.renderers import ProfileJSONRenderer


class IslandProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v0/island'


class NodeProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v0/node'


class ServerProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v0/server'
