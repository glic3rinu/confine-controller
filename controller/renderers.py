from __future__ import absolute_import

from controller.apps.api.renderers import ProfileJSONRenderer


class BaseProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v1/base'
