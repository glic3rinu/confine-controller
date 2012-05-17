"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User

from user_management import forms
from user_management import models
from user_management import user_management_utils as utils

from slices import models as slice_models

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class UserManagementTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.request_headers = { 'HTTP_HOST': 'testserver' }

    def test_right_registration(self):
        """
        Test to check if registration works with right params
        """
        before_users = User.objects.all().count()

        username = "username"
        password = "password"
        email = "test@test.org"

        args = {'username': username,
                'password': password,
                're_password': password,
                'email': email}
        response = self.client.post("/register/",
                                    args,
                                    **self.request_headers
                                    )

        self.assertEqual(response.status_code,
                         200)
        after_users = User.objects.all().count()
        self.assertEqual(before_users+1, after_users)

    def test_wrong_registration(self):
        """
        Test to check if registration form is giving right feedback on error cases
        """
        username = "username"
        password = "password"
        wrong_password = "badpassword"
        email = "test@test.org"
        wrong_email = "test"

        form = forms.RegisterForm(initial = {
            'username': username,
            'password': password,
            'email': email
            })
        self.assertFalse(form.is_valid())

        form = forms.RegisterForm(initial = {
            'username': username,
            'password': password,
            're_password': wrong_password,
            'email': email
            })
        self.assertFalse(form.is_valid())

        form = forms.RegisterForm(initial = {
            'username': username,
            'password': password,
            're_password': password,
            'email': wrong_email
            })
        self.assertFalse(form.is_valid())

    def test_user_delete_request(self):
        """
        Test if user delete request is created correctly
        """
        user, username, password, mail = self.create_user()

        user = self.client.login(username=username, password=password)
        args = {}
        response = self.client.get("/delete_user/",
                                    args,
                                    **self.request_headers
                                    )
        self.assertEqual(response.status_code,
                         200)
        self.assertTrue(User.objects.get(username = username).is_active)

        args['delete'] = 'no'
        before_delete_requests = models.DeleteRequest.objects.all().count()
        response = self.client.get("/delete_user/",
                                   args,
                                   **self.request_headers
                                   )
        after_delete_requests = models.DeleteRequest.objects.all().count()
        self.assertEqual(before_delete_requests, after_delete_requests)
        self.assertRedirects(response,
                             '/')

        args['delete'] = 'yes'
        response = self.client.get("/delete_user/",
                                   args,
                                   **self.request_headers
                                   )
        after_delete_requests = models.DeleteRequest.objects.all().count()
        self.assertEqual(before_delete_requests+1, after_delete_requests)
        self.assertRedirects(response,
                             '/')

    def test_user_profile(self):
        """
        Test if user profile is updating correctly
        """
        user, username, password, mail = self.create_user()

        first_name = "fname"
        last_name = "lname"
        ssh_key = "key"

        user = self.client.login(username=username, password=password)
        args = {"first_name": first_name,
                "last_name": last_name,
                "ssh_key": ssh_key}
        response = self.client.post("/profile/",
                                    args,
                                    **self.request_headers
                                    )
        self.assertEqual(response.status_code,
                         200)

        n_user = User.objects.get(username = username)
        self.assertEqual(n_user.first_name, first_name)
        self.assertEqual(n_user.last_name, last_name)
        self.assertEqual(n_user.get_profile().ssh_key, ssh_key)


    def test_change_user_password(self):
        """
        Test if password is changed correctly
        """
        user, username, password, mail = self.create_user()
        user = self.client.login(username=username, password=password)
        new_password = "new_password"
        args = {"password": new_password,
                "re_password": new_password}
        response = self.client.post("/change_user_password/",
                                    args,
                                    **self.request_headers
                                    )
        self.assertEqual(response.status_code,
                         200)
        self.client.logout()

        self.assertTrue(self.client.login(
            username=username,
            password=new_password))


    def test_has_permission_system(self):
        user, uname, passw, mail = self.create_user()
        user2, uname2, passw2, mail2 = self.create_user(username = "username2",
                                                        email = "username2@test.org")
        user3, uname3, passw3, mail3 = self.create_user(username = "username3",
                                                        email = "username3@test.org")
        r1 = models.ResearchGroup(name = "r1")
        r1.save()
        r1.users.add(user)
        r1.users.add(user2)

        role1 = models.Role(research_group = r1,
                            name = "role1")
        role1.save()
        role1.users.add(user)
        role2 = models.Role(research_group = r1,
                            name = "role2")
        role2.save()
        role2.users.add(user2)
        role3 = models.Role(research_group = r1,
                            name = "role3")
        role3.save()

        slice1 = self.create_slice(user)

        perm_create = self.create_permission(slice1, "C", "C", [role1])
        perm_read = self.create_permission(slice1, "R", "R", [role1, role2])
        perm_update = self.create_permission(slice1, "U", "U", [role1])
        perm_delete = self.create_permission(slice1, "D", "D", [role1])
        perm_access = self.create_permission(slice1, "A", "A", [role1])
        
        
        self.assertTrue(utils.has_permission("slice_%i_C" % slice1.id, user))
        self.assertFalse(utils.has_permission("slice_%i_C" % slice1.id, user2))
        self.assertTrue(utils.has_permission("slice_%i_R" % slice1.id, user2))
                
        
    def create_user(self,
                    username = "username",
                    password = "password",
                    email = "test@test.org"):
        user = User.objects.create_user(
            username = username,
            password = password,
            email = email
            )
        user.is_active = True
        user.save()
        return [user, username, password, email]
        
    def create_slice(self,
                     user,
                     name = "name"):
        c_slice = slice_models.Slice(user = user,
                                     name = name)
        c_slice.save()
        return c_slice

    def create_permission(self,
                          entity,
                          name,
                          permission,
                          roles = []):
        
        perm = models.ConfinePermission(name = name,
                                        permission = permission)
        perm.entity = entity
        perm.save()
        for role in roles:
            perm.role.add(role)
        return perm
