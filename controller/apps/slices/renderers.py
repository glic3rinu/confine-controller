from __future__ import absolute_import

from api.renderers import ProfileJSONRenderer


class SliceProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v1/slice'


class SliverProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v1/sliver'


class TemplateProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v1/template'
