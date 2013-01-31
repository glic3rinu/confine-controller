from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from groupregistration.models import GroupRegistration
from users.models import Group, User


SERVER_URL = 'http://testserver'

def test_reverse(viewname, urlconf=None, args=None, kwargs=None):
    return SERVER_URL + reverse(viewname, urlconf, args, kwargs)

"""
Tests:
    1. form registration
        a. not logged
        b. logged
        [show form + objects creation + mail sent]
    2. admin
        a. list
        b. approve
        c. reject
"""

class FormTestCase(TestCase):
    """
    Test the interaction with the group registration form
    used for requesting the registration of a new group in
    the testbed.

    """

    def test_form(self):
        """
        Test if the group registration form is generated
        successfully

        """
        url = reverse('registration_group_register')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertTrue('user_form' in resp.context)

    def test_form_post(self):
        """
        Test that a valid post for creating a new group
        registration is working properly, for a unregistered
        user

        """
        url = reverse('registration_group_register')
        post = {
            'name': 'somegroup',
            'description': '',
            'user-username': 'confine',
            'user-email': 'confine@yopmail.com',
            'user-password1': 'secret',
            'user-password2': 'secret',
        }
        resp = self.client.post(url, post)
        url_complete = test_reverse('registration_group_complete')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], url_complete)

        # test if the objects has been created succesfully:
        # Group, User and GroupRegistration
        qs_group = Group.objects.filter(name='somegroup')
        qs_user  = User.objects.filter(username='confine')
        self.assertTrue(qs_group.exists())
        self.assertTrue(qs_user.exists())

        group = qs_group.get()
        user  = qs_user.get()
        qs_gr = GroupRegistration.objects.filter(group=group, user=user)
        self.assertTrue(qs_gr.exists())
        self.assertFalse(group.is_approved)
        self.assertFalse(user.is_active)
        
    def test_form_post_bad(self):
        """
        Check if the server gives a valid response for a bad
        post request of the group registration form (not all
        mandatory fields provided)

        """
        url = reverse('registration_group_register')

        # Send no POST data
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

        # Send junk POST data
        post = {
            #'name': '',
            'description': '',
            'user-username': 'confine',
            'user-email': 'confine.a.com',
            'user-password1': 'secret',
            'user-password2': 'secret',
        }
        resp = self.client.post(url, post)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['form']['name'].errors)


    def test_form_post_logged(self):
        """
        Test a group registration request from a logged user.
        """
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')

        url = reverse('registration_group_register')
        post = {
            'name': 'somegroup',
            'description': '',
        }
        resp = self.client.post(url, post)
        url_complete = test_reverse('registration_group_complete')

        # check server response
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], url_complete)

        # check models creation
        qs_group = Group.objects.filter(name='somegroup')
        self.assertTrue(qs_group.exists())

        group = qs_group.get()
        qs_gr = GroupRegistration.objects.filter(group=group, user=user)
        self.assertTrue(qs_gr.exists())

        #user.email_user(self, 'subject', 'message') #debug_DELETE_ME
        #self._test_mails_sent(2) #FIXME 2 mails must be sent: operators and user

    def _test_mails_sent(self, count):
        #TODO something is not working properly
        #       the emails sent are not in the mail.outbox
        self.assertEquals(len(mail.outbox), count)


class AdminViewsTestCase(TestCase):
    fixtures = ['rg_testdata.json']

    def setUp(self):
        """
        By default the tests are executed as superuser
        
        """
#        User.objects.create_superuser('admin', 'admin@test.com', 'adminpassword')
#        User.objects.create_user('user', 'user@test.com', 'userpassword')
        self._login(superuser=True)

    def test_admin_list(self):
        """ List the group registration """
        url = reverse('admin:groupregistration_groupregistration_changelist')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # and now as normal user (forbidden)
        self._login()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_admin_approve(self):
        """ Approve a group registration """
        gr = GroupRegistration.objects.get(pk=1)
        url = reverse('admin:groupregistration_groupregistration_approve', args=[gr.id])
        resp = self.client.get(url)

        url_changelist = test_reverse('admin:groupregistration_groupregistration_changelist')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], url_changelist)

        # check if approve gr has proper side effects
        self.assertTrue(gr.group.is_approved)
        self.assertTrue(gr.user.is_active)
        self.assertTrue(gr.group.has_roles(gr.user, ['admin']))
    
    def test_admin_reject(self):
        """ Reject a group registration """
        gr = GroupRegistration.objects.get(pk=1)
        uid = gr.user.id
        gid = gr.group.id

        url = reverse('admin:groupregistration_groupregistration_reject', args=[gr.id])
        resp = self.client.get(url)

        url_changelist = test_reverse('admin:groupregistration_groupregistration_changelist')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], url_changelist)

        # check if reject gr has proper side effects
        # if the user was inactive then should be removed
        if User.objects.filter(pk=uid).exists():
            self.assertTrue(gr.user.is_active)

        self.assertFalse(Group.objects.filter(pk=gid).exists())
        self.assertFalse(GroupRegistration.objects.filter(pk=1).exists())

    def ztest_admin_not_exist(self):
        """ Access to a not existent object """
        # TODO BUG: when an object does not exists --> 404!!
        url = reverse('admin:groupregistration_groupregistration_approve', args=[10])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


    def _login(self, superuser=False):
        self.client.logout()
        if superuser:
            self.client.login(username='confine', password='confine')
        else:
            self.client.login(username='john', password='secret')
        
