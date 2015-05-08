from __future__ import absolute_import

from controller.apps.api.renderers import ProfileJSONRenderer


class BaseImageProfileRenderer(ProfileJSONRenderer):
    profile = 'http://confine-project.eu/schema/controller/v1/baseimage'
