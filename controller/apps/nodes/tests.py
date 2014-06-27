"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse
from django.test import TestCase

from users.models import User
from .models import Island


class IslandTest(TestCase):
    def setUp(self):
        self.password = 'vct'
        self.user = User.objects.create_superuser(username='vct', name='vct',
            email='vct@localhost', password=self.password)
        self.client.login(username=self.user.username, password=self.password)
    
    def test_changeview(self):
        # Test island changeview (regression on #157 rev 1974935d)
        island = Island.objects.create(name='Island', description='Island to test changeview.')
        island_url = reverse('admin:nodes_island_change', args=(island.pk,))
        resp = self.client.get(island_url)
        self.assertTrue(200, resp.status_code)
