from __future__ import absolute_import

from api.renderers import ProfileJSONRenderer


class SliceProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v0/slice'


class SliverProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v0/sliver'


class TemplateProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v0/template'
