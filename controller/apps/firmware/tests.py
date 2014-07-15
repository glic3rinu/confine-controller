"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from nodes.models import Node
from users.models import Group

from .models import Build
from .settings import FIRMWARE_BUILD_IMAGE_STORAGE

class BuildTest(TestCase):
    def test_handle_access_denied_image_file(self):
        group = Group.objects.create(name='group', allow_nodes=True)
        node = Node.objects.create(name='node', group=group)
        build = Build.objects.create(node=node, task_id='926ec44c-4842-417b-a45d-4b7c858888cf')
        # Point image outside of FIRMWARE_BUILD_IMAGE_STORAGE
        build.image.name = FIRMWARE_BUILD_IMAGE_STORAGE.location + '../image.tgz'
        try:
            build.state
        except SuspiciousFileOperation:
            self.failureException
