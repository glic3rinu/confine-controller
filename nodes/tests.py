"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client

from nodes import models
from nodes import examples

from xml.etree import ElementTree

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class XMLTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.request_headers = { 'HTTP_HOST': 'myhost.com' }
        
    def test_right_upload_node(self):
        """
        Test to check if upload node view works well with right node info
        """
        before_nodes = models.Node.objects.all().count()

        args = {'node_data': examples.UPLOAD_NODE_DATA}
        response = self.client.post("/upload_node/",
                                    args,
                                    **self.request_headers
                                    )

        self.assertEqual(response.status_code,
                         200)
        
        after_nodes = models.Node.objects.all().count()
        self.assertEqual(before_nodes+1, after_nodes)
