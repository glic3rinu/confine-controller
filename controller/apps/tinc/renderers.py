from __future__ import absolute_import

from controller.apps.api.renderers import ProfileJSONRenderer


class HostProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/registry/v1/host'
