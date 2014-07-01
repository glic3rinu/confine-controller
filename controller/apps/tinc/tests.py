"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from nodes.models import Island, Server

from .models import TincAddress


class TincAddressTest(TestCase):
    
    def test_delete_behaviour(self):
        # Check deletion behaviour #487
        island = Island.objects.create(name="RandomIsland")
        server = Server.objects.create(description="A server")
        tinc_addr = TincAddress.objects.create(addr='1.0.0.1', host=server.tinc,
            island=island)
        
        island.delete()
        try:
            tinc_addr = TincAddress.objects.get(pk=tinc_addr.pk)
        except TincAddress.DoesNotExist:
            self.fail("TincAddress has been removed!")
        self.assertIsNone(tinc_addr.island)
