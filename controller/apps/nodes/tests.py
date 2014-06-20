"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from nodes.models import Island, Server, ServerApi


class SimpleTest(TestCase):
    def test_delete_behaviour(self):
        # Check deletion behaviour #487
        island = Island.objects.create(name="RandomIsland")
        server = Server.objects.create(description="A server")
        server_api = ServerApi.objects.create(type=ServerApi.REGISTRY,
            server=server, island=island)
        
        island.delete()
        try:
            server_api = ServerApi.objects.get(pk=server_api.pk)
        except ServerApi.DoesNotExist:
            self.fail("ServerApi has been removed!")
        self.assertIsNone(server_api.island)
