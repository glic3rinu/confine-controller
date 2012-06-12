"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client

from nodes import models
from nodes import examples

from nodes import node_utils as utils
from nodes import api
from nodes import settings as node_settings

from slices import models as slices_models

from xml.etree import ElementTree

from django.contrib.auth.models import User

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class APITest(TestCase):
    def setUp(self):
        pass

    def test_get_node(self):
        """
        Test get_node api call
        """
        right_hostname = "hostname"
        wrong_hostname = "no name"
        node = self.create_test_node(hostname = right_hostname)
        self.assertEqual(node.id, api.get_node({'hostname': right_hostname}).id)
        self.assertEqual(None, api.get_node({'hostname': wrong_hostname}))
        

    def test_edit_node(self):
        """
        Test edit_node api call
        """
        pass


    def test_set_node(self):
        """
        Test set_node api call
        """
        node = self.create_test_node(commit = False)
        storage = self.create_test_storage(commit = False)
        memory = self.create_test_memory(commit = False)
        cpu = self.create_test_cpu(commit = False)
        iface1 = self.create_test_interface(commit = False)
        iface2 = self.create_test_interface(commit = False)

        self.assertTrue(api.set_node({'node': node,
                                      'storage': storage,
                                      'memory': memory,
                                      'cpu': cpu,
                                      'interfaces': [iface1, iface2]}))
    

    def test_create_node(self):
        """
        Test create_node api call
        """
        before_nodes = models.Node.objects.all().count()
        self.assertTrue(api.create_node(examples.NODE_CREATION))
        after_nodes = models.Node.objects.all().count()
        self.assertEqual(before_nodes+1, after_nodes)

    def test_get_nodes(self):
        """
        Test get_nodes api call
        """
        pass

    def test_delete_node(self):
        """
        Test delete_node api call
        """
        node1 = self.create_test_node()
        before_requests = models.DeleteRequest.objects.all().count()
        self.assertTrue(api.delete_node({'hostname': node1.hostname}))
        after_requests = models.DeleteRequest.objects.all().count()
        self.assertEqual(before_requests+1, after_requests)

        
    def test_create_slice(self):
        """
        Test create slice api call
        """
        node1 = self.create_test_node(hostname = "hostname1",
                                 ip = "1.1.1.1")
        node2 = self.create_test_node(hostname = "hostname2",
                                 ip = "1.1.1.2")
        node3 = self.create_test_node(hostname = "hostname3",
                                 ip = "1.1.1.3")
        before_slices = slices_models.Slice.objects.all().count()
        before_slivers = slices_models.Sliver.objects.all().count()

        name = 'slice_test'
        user = self.create_user()
        node_info = {}
        node_info[node1.id] = {'networks': [],
                               'cpu': None,
                               'storage': None,
                               'memory': None}
        node_info[node2.id] = {'networks': [],
                               'cpu': None,
                               'storage': None,
                               'memory': None}
        node_info[node3.id] = {'networks': [],
                               'cpu': None,
                               'storage': None,
                               'memory': None}
        slice_params = {
            'nodes': node_info,
            'name': name,
            'user': user
            }
        self.assertTrue(api.create_slice(slice_params))

        after_slices = slices_models.Slice.objects.all().count()
        after_slivers = slices_models.Sliver.objects.all().count()

        self.assertEqual(before_slices+1, after_slices)
        self.assertEqual(before_slivers+3, after_slivers)

        c_slice = slices_models.Slice.objects.get(name = name)
        self.assertEqual(c_slice.sliver_set.all().count(), 3)

        self.assertEqual(node1.sliver_set.all().count(), 1)
        self.assertEqual(node2.sliver_set.all().count(), 1)
        self.assertEqual(node3.sliver_set.all().count(), 1)

    def test_show_slices(self):
        """
        Test show_slices api call
        """
        user1 = self.create_user()
        user2 = self.create_user(username = "user2",
                                 mail = "user2@test.com")

        name1 = "name1"
        name2 = "name2"
        name3 = "name3"
        
        slice1 = self.create_slice(user = user1, name=name1)
        slice1 = self.create_slice(user = user1, name=name2)
        slice1 = self.create_slice(user = user2, name=name3)

        user1_slices = api.show_slices({'user': user1})
        user2_slices = api.show_slices({'user': user2})

        self.assertEqual(user1_slices.count(), 2)
        self.assertEqual(user2_slices.count(), 1)

    def test_get_node_configuration(self):
        """
        Test get_node_configuration api call
        """
        user = self.create_user()
        name = "slice1"
        node = self.create_test_node()
        slice1 = self.create_slice(user, name)
        sliver1 = self.create_sliver(node, slice1)

        params = {'hostname': node.hostname}
        self.assertNotEqual(api.get_node_configuration(params), "")

    def test_get_node_public_keys(self):
        """
        Test get_node_public_keys api call
        """
        pass

    def test_get_slice_public_keys(self):
        """
        Test get_slice_public_keys api call
        """
        pass

    def test_delete_sliver(self):
        """
        Test delete_sliver api call
        """
        pass

    def create_sliver(self, c_node, c_slice):
        sliver = slices_models.Sliver(slice = c_slice,
                                      node = c_node)
        sliver.save()
        return sliver

    def create_slice(self, user, name):
        new_slice = slices_models.Slice(name = name,
                                       user = user)
        new_slice.save()
        return new_slice
        
    def create_test_node(self,
                         hostname = "hostname",
                         ip = "1.1.1.1",
                         architecture = "x86_generic",
                         commit = True):
        node = models.Node(hostname = hostname,
                           ip = ip,
                           architecture = architecture,
                           state = node_settings.ONLINE)
        if commit:
            node.save()
        return node

    def create_test_storage(self,
                            types = "debian-squeeze-amd64",
                            size = 64,
                            node = None,
                            commit = True):
        storage = models.Storage(types = types,
                                 size = size)
        if node:
            storage.node = node
        if commit:
            storage.save()
        return storage

    def create_test_memory(self,
                           size = 64,
                           node = None,
                           commit = True):
        memory = models.Memory(size = size)
        if node:
            memory.node = node
        if commit:
            memory.save()
        return memory

    def create_test_cpu(self,
                        model = "intel x86",
                        number = 1,
                        frequency = "64",
                        node = None,
                        commit = False):
        cpu = models.CPU(model = model,
                         number = number,
                         frequency = frequency)
        if node:
            cpu.node = node
        if commit:
            cpu.save()
        return cpu

    def create_test_interface(self,
                              name = "eth0",
                              itype = "802.3u",
                              node = None,
                              commit = True): 
        interface = models.Interface(name = name,
                                     type = itype)
        if node:
            interface.node = node
        if commit:
            interface.save()
        return interface
    
    def create_user(self,
                    username = "fakename",
                    mail = "fake@pukkared.com",
                    password = "mypassword"):
        user = User.objects.create_user(username, mail, password)
        return user

class XMLTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.request_headers = { 'HTTP_HOST': 'testserver' }
        
    def test_right_upload_node(self):
        """
        Test to check if upload node view works well with right node info
        """
        before_nodes = models.Node.objects.all().count()

        args = {'node_data': examples.UPLOAD_NODE_DATA}
        response = self.client.post("/upload_node/xml/",
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
        response = self.client.post("/delete_node/xml/",
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
        response = self.client.post("/get_node_configuration/xml/",
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
        response = self.client.post("/get_node_public_keys/xml/",
                                    args,
                                    **self.request_headers
                                    )
        self.assertEqual(response.status_code,
                         200)

        tree = ElementTree.fromstring(response.content)
        self.assertEqual('1', tree.find('key_request').text)


class HTMLTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.request_headers = { 'HTTP_HOST': 'testserver' }
        
    def test_index(self):
        """
        Test to check if index is beign returned without conflicts
        """
        args = {}
        response = self.client.get("/",
                                   args,
                                   **self.request_headers
                                   )
        self.assertEqual(response.status_code,
                         200)

    def test_node_index(self):
        """
        Test to check if index is beign returned without conflicts
        """
        args = {}
        response = self.client.get("/node_index/",
                                   args,
                                   **self.request_headers
                                   )
        self.assertEqual(response.status_code,
                         200)

    def test_show_own_slices(self):
        """
        Test to check if index is beign returned without conflicts
        """
        username, password = self.create_user()
        user = self.client.login(username=username, password=password)
        
        args = {}
        response = self.client.get("/show_own_slices/",
                                   args,
                                   **self.request_headers
                                   )
        self.assertEqual(response.status_code,
                         200)

    def create_user(self,
                    username = "fakename",
                    mail = "fake@pukkared.com",
                    password = "mypassword"):
        User.objects.create_user(username, mail, password)
        return username, password

    def create_node(self,
                    hostname = "host",
                    ip = "1.1.1.1"):
        node = models.Node(hostname = hostname,
                           ip = ip)
        node.save()
        return node.id
