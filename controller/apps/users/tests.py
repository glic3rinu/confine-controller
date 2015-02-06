import re
import time
import unittest

from django.conf import settings
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from django.test.utils import override_settings
from urlparse import urlparse

from controller.utils.apps import is_installed, remove_app
from controller.tests import AuthenticatedTestCase

from users.models import Group, Roles, User, ResourceRequest, JoinRequest
from users.registration.forms import RegistrationFormUniqueEmail as RegistrationForm


def url_path(url):
    return urlparse(url).path


class GroupFormTestCase(AuthenticatedTestCase):
    """
    Test the interaction with the group registration form
    used for requesting the registration of a new group in
    the testbed.

    """
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
            'roles-TOTAL_FORMS': 0,
            'roles-INITIAL_FORMS': 0,
            'roles-MAX_NUM_FORMS': 0,
            'join_requests-TOTAL_FORMS': 0,
            'join_requests-INITIAL_FORMS': 0,
            'join_requests-MAX_NUM_FORMS': 0,
        }
        resp = self.client.post(url, post)
        url_relative = reverse('admin:users_group_changelist')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(url_path(resp['Location']), url_relative)

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
            'request_nodes': True,
            'roles-TOTAL_FORMS': 0,
            'roles-INITIAL_FORMS': 0,
            'roles-MAX_NUM_FORMS': 0,
            'join_requests-TOTAL_FORMS': 0,
            'join_requests-INITIAL_FORMS': 0,
            'join_requests-MAX_NUM_FORMS': 0,
        }
        resp = self.client.post(url, post)
        url_relative = reverse('admin:users_group_changelist')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(url_path(resp['Location']), url_relative)

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
        Roles.objects.create(group=group, user=user, is_group_admin=True)

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
        # create the request
        group = Group.objects.get(pk=1)
        ResourceRequest.objects.create(group=group, resource='slices')

        # The group has a resource requests
        qs_req  = ResourceRequest.objects.filter(group=group, resource='slices')
        self.assertTrue(qs_req.exists(), "Group doesn't have resource requests.")

        self._login(superuser=True) # only operator can change resources allowed
        url = reverse('admin:users_group_change', args=[group.id])
        post = {
            'name': group.name,
            'description': group.description,
            'allow_nodes': group.allow_nodes,
            'allow_slices': True,
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


class GroupJoinTestCase(AuthenticatedTestCase):
    """ Join request (to a group) tests """

    def test_create_join_request(self):
        self._login()
        gid = 1
        uid = self.client.session['_auth_user_id']

        url = reverse('admin:users_group_join-request', args=[gid])
        post = {
            'action': 'join_request',
            'post': 'generic_confirmation',
            '_selected_action': 1,
        }
        resp = self.client.post(url, post)
        url_relative = reverse('admin:users_group_change', args=[gid])
    
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(url_path(resp['Location']), url_relative)

        self.assertTrue(JoinRequest.objects.filter(user=uid, group=gid).exists())

    def _do_action_join_request(self, action, roles=[]):
        self.test_create_join_request() #create a JoinRequest
        uid = 3
        gid = 1
        jid = JoinRequest.objects.get(user=uid, group=gid).pk
        
        self._login(admin=True)
        url = reverse('admin:users_group_change', args=[gid])
        resp = self.client.get(url)
        group_form = resp.context['adminform'].form
        post = {
            "name": group_form['name'].value(),
            "description": group_form['description'].value(),
            "request_slices": group_form['request_slices'].value(),
            "request_nodes": group_form['request_nodes'].value(),
            #roles formset
            "roles-TOTAL_FORMS": 1,
            "roles-0-id": 8,
            "roles-0-group": 1,
            "roles-0-is_group_admin": "on",
            "roles-INITIAL_FORMS": 1,
            "roles-MAX_NUM_FORMS": 1000,
            #joinrequest formset
            "join_requests-TOTAL_FORMS": 1,
            "join_requests-INITIAL_FORMS": 1, 
            "join_requests-MAX_NUM_FORMS": 0,
            "join_requests-0-id": jid,
            "join_requests-0-group": gid,
            "join_requests-0-roles": roles,
            "join_requests-0-action": action, 
            "_save": "Save" #admin submit action
        }
        resp = self.client.post(url, post)
        url_relative = reverse('admin:users_group_changelist')
        
        # redirect after posting
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(url_path(resp['Location']), url_relative)

        # join requests not exists 
        self.assertFalse(JoinRequest.objects.filter(user=uid, group=gid).exists())


    def test_join_request_accept(self):
        uid = 3
        gid = 1
        self._do_action_join_request(action='accept', roles=['slice_admin'])

        # has been created a role to user at the group
        roles_qs = Roles.objects.filter(user=uid, group=gid)
        self.assertTrue(roles_qs.exists())
        self.assertTrue(roles_qs.get().is_slice_admin)

    def test_join_request_reject(self):
        uid = 3
        gid = 1
        self._do_action_join_request('reject')
        
    def test_join_request_ignore(self):
        uid = 3
        gid = 1
        self._do_action_join_request('ignore')


@unittest.skipUnless(is_installed('registration'), "django-registration is required")
class RegistrationTestCase(AuthenticatedTestCase):
    
    @unittest.skipIf(is_installed('captcha'), "remove 'captcha' from INSTALLED_APPS for properly run this test.")
    @override_settings(USERS_REGISTRATION_MODE = 'RESTRICTED',
        MAIL_REGISTRATION_APPROVE = 'vct@localhost')
        # Removing captcha doesn't seems to work
        #INSTALLED_APPS = remove_app(settings.INSTALLED_APPS, 'captcha'))
    def test_notify_operators(self):
        self.client.logout()
        self.assertFalse(is_installed('captcha'))
        name = "user" + str(int(round(time.time() * 1000)))
        password = "foopass"
        data = {
            "name": name,
            "username": name,
            "email": name + "@localhost",
            "password1": password,
            "password2": password,
        }
        response = self.client.post(reverse('registration_register'), data=data)
        self.assertRedirects(response, reverse('registration_complete'))
        
        # registration successful sends an email with confirmation URL
        self.assertEquals(len(mail.outbox), 1)
        URL_REGEX = 'http[s]?://\w+/accounts/activate/\w+'
        urls = re.findall(URL_REGEX, mail.outbox[0].body)
        self.assertEquals(len(urls), 1)
        mail.outbox = []
        
        # Confirm user email
        response = self.client.get(urls[0], follow=True)
        self.assertRedirects(response, reverse('registration_activation_complete'), status_code=301)
        
        # One email to operators should be sent requesting approvation
        self.assertEquals(len(mail.outbox), 1)
        self.assertTrue(settings.MAIL_REGISTRATION_APPROVE, mail.outbox[0].to)
        
        # The email contains the user URL
        URL_REGEX = 'http[s]?://\w+/admin/users/user/\d+/'
        urls = re.findall(URL_REGEX, mail.outbox[0].body)
        self.assertEquals(len(urls), 1)
        mail.outbox = []
        
        # Mark user as active
        user = User.objects.get(name=name)
        user.is_active = True
        user.save()
        
        # Two emails should be sent: one to user and another to operators
        self.assertEquals(len(mail.outbox), 2)
        self.assertTrue(user.email in mail.outbox[0].to)
        self.assertTrue(settings.MAIL_REGISTRATION_APPROVE, mail.outbox[1].to)
        
        # Registered user should be able to login
        self.client.login(username=name, password=password)
        response = self.client.get(reverse('admin:index'))
        self.assertEquals(response.status_code, 200)
    
    def test_registration_form(self):
        """Test registration form validation."""
        # Create user to validate duplicated username, name, email
        User.objects.create(name='Frank', email='frank@localhost', username='frank')
        
        # Define valid data for user registration
        data = {
            'name': 'Name Lastname',
            'username': 'name.lastname',
            'email': 'name.lastname@localhost',
            'password1': 's3cr3t',
            'password2': 's3cr3t',
        }
        
        # check form with valid data
        form = RegistrationForm(data=data)
        self.assertTrue(form.is_valid())
        
        # check form with valid but uncommon e-mail address
        data_test = data.copy()
        data_test['email'] = 'name.lastname+suffix@localhost' # a plus sign is valid!
        form = RegistrationForm(data=data_test)
        self.assertTrue(form.is_valid())
        
        # doesn't validate with invalid username
        data_test = data.copy()
        data_test['username'] = 'Some invalid username' # spaces not accepted
        form = RegistrationForm(data=data_test)
        self.assertFalse(form.is_valid(), "Invalid username shouldn't validate.")
        
        # check invalid email validation
        data_test = data.copy()
        data_test['email'] = 'invalid-email'
        form = RegistrationForm(data=data_test)
        self.assertFalse(form.is_valid(), "Invalid email shouldn't validate.")
        
        # check duplicated username
        data_test = data.copy()
        data_test['username'] = 'frank'
        form = RegistrationForm(data=data_test)
        self.assertFalse(form.is_valid(), "Duplicated username shouldn't validate.")
        
        # check duplicated name
        data_test = data.copy()
        data_test['name'] = 'Frank'
        form = RegistrationForm(data=data_test)
        self.assertFalse(form.is_valid(), "Duplicated name shouldn't validate.")
        
        # check duplicated email
        data_test = data.copy()
        data_test['email'] = 'frank@localhost'
        form = RegistrationForm(data=data_test)
        self.assertFalse(form.is_valid(), "Duplicated email shouldn't validate.")
        
        # check not matching passwords
        data_test = data.copy()
        data_test['password2'] = 'pass-not-matchs!'
        form = RegistrationForm(data=data_test)
        self.assertFalse(form.is_valid(), "Different passwords shouldn't validate.")
    
    def test_registration_admin_search(self):
        """
        Test registration profile admin search with custom
        user model (#518).
        """
        self._login(superuser=True)
        url = reverse('admin:registration_registrationprofile_changelist')
        resp = self.client.get(url, {'q': 'foo'})
        self.assertEquals(resp.status_code, 200)


class GroupAdminTests(TransactionTestCase):
    # TODO(santiago): reimplement tests a higher level.
    # It's not possible to difference at model level these situations:
    # a) Try to delete group, includes deleting group admin, it's OK
    #    but raises Error because group doesn't have group admin.
    #    Django deletes first the user (group admin), then the group.
    # b) Try to delete group admin, raise Error (OK)
    
    def test_delete_last_group_admin_user(self):
        # We shouldn't be able to delete a group admin if is the last one.
        group = Group.objects.create(name='group')
        user = User.objects.create_user('user', 'user@localhost', name='user')
        Roles.objects.create(group=group, user=user, is_group_admin=True)
        
        self.assertRaises(PermissionDenied, user.delete)
        self.assertTrue(group.roles.filter(is_group_admin=True).exists())
    
    def test_delete_last_group_admin_role(self):
        # We shouldn't be able to delete a group admin if is the last one.
        group = Group.objects.create(name='group')
        user = User.objects.create_user('user', 'user@localhost', name='user')
        rol = Roles.objects.create(group=group, user=user, is_group_admin=True)
        
        self.assertRaises(PermissionDenied, rol.delete)
        self.assertTrue(group.roles.filter(is_group_admin=True).exists())
    
    def test_delete_a_group_admin_user(self):
        # We should be able to delete a group admin if there is others.
        group = Group.objects.create(name='group')
        user = User.objects.create_user('user', 'user@localhost', name='user')
        user2 = User.objects.create_user('user2', 'user2@localhost', name='user2')
        Roles.objects.create(group=group, user=user, is_group_admin=True)
        Roles.objects.create(group=group, user=user2, is_group_admin=True)
        
        user.delete()
        self.assertTrue(group.roles.filter(is_group_admin=True).exists())
        self.assertFalse(group.roles.filter(is_group_admin=True, user=user).exists())
    
    def test_delete_a_group_admin_role(self):
        # We should be able to delete a group admin if there is others.
        group = Group.objects.create(name='group')
        user = User.objects.create_user('user', 'user@localhost', name='user')
        user2 = User.objects.create_user('user2', 'user2@localhost', name='user2')
        rol = Roles.objects.create(group=group, user=user, is_group_admin=True)
        Roles.objects.create(group=group, user=user2, is_group_admin=True)
        
        rol.delete()
        self.assertTrue(group.roles.filter(is_group_admin=True).exists())
        self.assertFalse(group.roles.filter(is_group_admin=True, user=user).exists())
    
    def test_delete_group(self):
        group = Group.objects.create(name='group')
        user = User.objects.create_user('user', 'user@localhost', name='user')
        Roles.objects.create(group=group, user=user, is_group_admin=True)
        
        group.delete()
        self.assertFalse(group.roles.filter(is_group_admin=True, user=user).exists())
