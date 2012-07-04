"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from ticket_system import models
from django.contrib.auth.models import User
import datetime

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class TicketSystemTest(TestCase):

    def setUp(self):
        self.create_queue(name = "queue1")
        self.create_queue(name = "queue2")
        self.client = Client()
        self.request_headers = {'HTTP_HOST': 'testserver'}

    def test_show_tickets(self):
        """
        Test to check if show_tickets is beign returned without problems
        """
        username, password = self.create_user()
        user = self.client.login(username=username, password=password)
        args = {}
        response = self.client.get("/ticket_system/",
                                   args,
                                   **self.request_headers
                                   )
        self.assertEqual(response.status_code,
                         200)

    def test_show_ticket(self):
        """
        Test to check if show_ticket is beign returned without problems
        """
        username, password = self.create_user()
        user = self.client.login(username=username, password=password)
        args = {}

        ticket = self.create_ticket(creator = User.objects.get(username = username),
                                    queue = models.Queue.objects.all()[0])
        response = self.client.get("/ticket_system/ticket/%i/" % ticket.id,
                                   args,
                                   **self.request_headers
                                   )
        self.assertEqual(response.status_code,
                         200)

    def test_show_ticket_add_message(self):
        """
        Test to check if show_ticket add_message functionality is working
        """
        username, password = self.create_user()
        user = self.client.login(username=username, password=password)
        args = {
            'visibility': 'Public',
            'content': 'content'
                }

        ticket = self.create_ticket(creator = User.objects.get(username = username),
                                    queue = models.Queue.objects.all()[0])
        previous_messages = ticket.message_set.all().count()
        response = self.client.post("/ticket_system/ticket/%i/" % ticket.id,
                                   args,
                                   **self.request_headers
                                   )
        self.assertRedirects(response, "/ticket_system/ticket/%i/" % ticket.id)
        after_messages = ticket.message_set.all().count()
        self.assertEqual(previous_messages+1, after_messages)

    def test_create_ticket(self):
        """
        Test to check if create_ticket is working
        """
                
        username, password = self.create_user()
        user = self.client.login(username=username, password=password)
        args = {}

        previous_tickets = models.Ticket.objects.all().count()
        response = self.client.get("/ticket_system/create_ticket/",
                                   args,
                                   **self.request_headers
                                   )
        self.assertEqual(response.status_code, 200)

        args = {
                'queue': models.Queue.objects.all()[0].id,
                'subject': 'subject',
                'content': 'content',
                'priority': 'Low',
                }

        previous_tickets = models.Ticket.objects.all().count()
        response = self.client.post("/ticket_system/create_ticket/",
                                   args,
                                   **self.request_headers
                                   )
        self.assertRedirects(response, "/ticket_system/")
        after_tickets = models.Ticket.objects.all().count()
        self.assertEqual(previous_tickets+1, after_tickets)

    def create_queue(self, name = "queue"):
        queue = models.Queue(name = name)
        queue.save()
        return queue

    def create_ticket(self,
                      creator = None,
                      queue = None,
                      subject = "subject",
                      content = "content",
                      priority = "High",
                      status = "New",
                      creation_date = datetime.datetime.now()):

        ticket = models.Ticket(creator = creator,
                               queue = queue,
                               subject = subject,
                               content = content,
                               priority = priority,
                               status = status,
                               creation_date = creation_date)
        ticket.save()
        return ticket

    def create_user(self,
                    username = "fakename",
                    mail = "fake@pukkared.com",
                    password = "mypassword"):
        User.objects.create_user(username, mail, password)
        return username, password
