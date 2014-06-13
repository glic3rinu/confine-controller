from __future__ import absolute_import

from django.test import TestCase
from django.db.models import get_app, get_models

from controller.admin.utils import get_modeladmin
from controller.utils.apps import is_installed

class UtilsTest(TestCase):
    def test_get_modeladmin(self):
        # Try to get every modeladmin from controller's models
        CONTROLLER_APPS = ['communitynetworks', 'firmware', 'gis', 'issues',
            'maintenance', 'monitor', 'nodes', 'notifications', 'pings',
            'resources', 'slices', 'state', 'tinc', 'users']
        for app_name in CONTROLLER_APPS:
            if not is_installed(app_name):
                continue
            app = get_app(app_name)
            for model in get_models(app):
                get_modeladmin(model)
