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
        tree = ElementTree.fromstring(response.content)
        
        self.assertEqual('1', tree.find('node_created').text)
        self.assertEqual(before_nodes+1, after_nodes)

    def test_right_delete_node_request(self):
        """
        Test to check if delete node request is processed in the right way
        """
        self.test_right_upload_node()
        
        before_nodes = models.Node.objects.all().count()
        before_requests = models.DeleteRequest.objects.all().count()
        
        args = {'node_data': examples.HOSTNAME_NODE_DATA}
        response = self.client.post("/delete_node/",
                                    args,
                                    **self.request_headers
                                    )

        self.assertEqual(response.status_code,
                         200)
        
        after_nodes = models.Node.objects.all().count()
        after_requests = models.DeleteRequest.objects.all().count()
        tree = ElementTree.fromstring(response.content)
        
        self.assertEqual(before_nodes, after_nodes)
        self.assertEqual(before_requests+1, after_requests)
        self.assertEqual('1', tree.find('delete_request').text)
        
    def test_right_config_file_retrieved(self):
        """
        Test to check if right config 
        """
        self.test_right_upload_node()
        
        args = {'node_data': examples.HOSTNAME_NODE_DATA}
        response = self.client.post("/get_node_configuration/",
                                    args,
                                    **self.request_headers
                                    )
        self.assertEqual(response.status_code,
                         200)

        tree = ElementTree.fromstring(response.content)
        self.assertEqual('1', tree.find('config_request').text)

    def test_right_config_file_generated(self):
        pass

    def test_right_keys_retrieved(self):
        """
        Test to check if right config 
        """
        self.test_right_upload_node()
        
        args = {'node_data': examples.HOSTNAME_NODE_DATA}
        response = self.client.post("/get_node_public_keys/",
                                    args,
                                    **self.request_headers
                                    )
        self.assertEqual(response.status_code,
                         200)

        tree = ElementTree.fromstring(response.content)
        self.assertEqual('1', tree.find('key_request').text)
