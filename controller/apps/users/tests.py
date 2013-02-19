from django.core.urlresolvers import reverse
from django.test import TestCase

from users.models import Group, Roles, User, ResourceRequest


SERVER_URL = 'http://testserver'

def test_reverse(viewname, urlconf=None, args=None, kwargs=None):
    return SERVER_URL + reverse(viewname, urlconf, args, kwargs)

"""
Tests:
    1. create group
        - without resource requests
        - with resource requests
    2. create requests in a group
    3. accept request
"""

class FormTestCase(TestCase):
    """
    Test the interaction with the group registration form
    used for requesting the registration of a new group in
    the testbed.

    """
    def setUp(self):
        """
        By default the tests are executed as normal user
        """
        User.objects.create_superuser('admin', 'admin@test.com', 'adminpassword')
        u = User.objects.create_user('user', 'user@test.com', 'userpassword')
        g = Group(name='group', description='foo')
        g.save()

        self._login()

    def test_add_form(self):
        """
        Test if the new group form is generated successfully

        """
        url = reverse('admin:users_group_add')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue('adminform' in resp.context)

    def test_create_no_resources(self):
        """
        Test that a valid post for creating a new group
        is working properly without resource requests

        """
        url = reverse('admin:users_group_add')
        post = {
            'name': 'somegroup',
            'description': 'somedescription',
        }
        resp = self.client.post(url, post)
        url_complete = test_reverse('admin:users_group_changelist')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], url_complete)

        # test if the objects has been created succesfully
        # and the group properly init
        qs_group = Group.objects.filter(name='somegroup')
        self.assertTrue(qs_group.exists())
        
        group = qs_group.get()
        self.assertFalse(group.allow_nodes)
        self.assertFalse(group.allow_slices)
        
        # group has admin and is the logged user
        user = User.objects.get(pk=self.client.session['_auth_user_id'])
        self.assertTrue(user in group.admins)

        qs_req  = ResourceRequest.objects.filter(group=group)
        self.assertFalse(qs_req.exists())

    def test_create_with_resources(self):
        """
        Test that a valid post for creating a new group
        is working properly with resource requests

        """
        url = reverse('admin:users_group_add')
        post = {
            'name': 'somegroup',
            'description': 'somedescription',
            'request_nodes': True
        }
        resp = self.client.post(url, post)
        url_complete = test_reverse('admin:users_group_changelist')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], url_complete)

        # test if the objects has been created succesfully
        # and the group properly init
        qs_group = Group.objects.filter(name='somegroup')
        self.assertTrue(qs_group.exists())
        
        group = qs_group.get()
        self.assertFalse(group.allow_nodes)
        self.assertFalse(group.allow_slices)

        # group has admin and is the logged user
        user = User.objects.get(pk=self.client.session['_auth_user_id'])
        self.assertTrue(user in group.admins)

        # test if the resource request has created
        qs_req  = ResourceRequest.objects.filter(group=group, resource='nodes')
        self.assertTrue(qs_req.exists())

    def test_resource_request_group(self):
        """ Update a group to create a new resource requests """
        group = Group.objects.get(pk=1)
        user = User.objects.get(pk=self.client.session['_auth_user_id'])

        ## add admin role to the user
        r = Roles(group=group, user=user, is_admin=True)
        r.save()

        url = reverse('admin:users_group_change', args=[group.id])
        post = {
            'name': group.name,
            'description': group.description,
            'allow_nodes': group.allow_nodes,
            'allow_slices': group.allow_slices,
            'request_nodes': False,
            'request_slices': True,
            'roles-TOTAL_FORMS': 0,
            'roles-INITIAL_FORMS': 0,
            'roles-MAX_NUM_FORMS': 0,
            'join_requests-TOTAL_FORMS': 0,
            'join_requests-INITIAL_FORMS': 0,
            'join_requests-MAX_NUM_FORMS': 0,
        }
        resp = self.client.post(url, post)
        self.assertEqual(resp.status_code, 200)
        
        # test if the resource request has created
        qs_req  = ResourceRequest.objects.filter(group=group, resource='slices')
        self.assertTrue(qs_req.exists())

    def test_accept_resource_request(self):
        """ Test if the operator can accept a resource requests """
        self.test_resource_request_group() #create the requests
        group = Group.objects.get(pk=1)

        # The group has a resource requests
        qs_req  = ResourceRequest.objects.filter(group=group, resource='slices')
        self.assertTrue(qs_req.exists())

        self._login(superuser=True) #only operator can change resources allowed
        url = reverse('admin:users_group_change', args=[group.id])
        post = {
            'name': group.name,
            'description': group.description,
            'allow_nodes': group.allow_nodes,
            'allow_slices': True,
#            'request_nodes': False,
#            'request_slices': True,
            'roles-TOTAL_FORMS': 0,
            'roles-INITIAL_FORMS': 0,
            'roles-MAX_NUM_FORMS': 0,
            'join_requests-TOTAL_FORMS': 0,
            'join_requests-INITIAL_FORMS': 0,
            'join_requests-MAX_NUM_FORMS': 0,
        }
        resp = self.client.post(url, post)
        self.assertEqual(resp.status_code, 200)

        # test if the resource request has created
        qs_req  = ResourceRequest.objects.filter(group=group, resource='slices')
        self.assertFalse(qs_req.exists())


    def _login(self, superuser=False):
        """ Login a user to the system """
        self.client.logout()
        if superuser:
            self.client.login(username='admin', password='adminpassword')
        else:
            self.client.login(username='user', password='userpassword')
