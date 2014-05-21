import time

from django.test import TestCase

from users.models import User
from .models import Message, Ticket


class TicketTest(TestCase):
    def setUp(self):
        name = self.randomString("user")
        self.user = User.objects.create(name=name, email=name + '@testserver')
    
    def randomString(self, prefix):
        return prefix+str(int(round(time.time() * 1000)))
    
    def test_ticket_on_user_deletion(self):
        """Test that author info is filled on user delete #289"""
        ticket = Ticket.objects.create(subject=self.randomString('ticket'),
            description='A ticket', created_by=self.user)
        self.assertEqual(ticket.created_by_name, '')
        
        message = Message.objects.create(ticket=ticket, author=self.user,
            content=self.randomString('A message'))
        self.assertEqual(message.author_name, '')
        
        self.user.delete()
        
        # check that user.name is stored after delete
        ticket = Ticket.objects.get(pk=ticket.pk)
        self.assertIsNone(ticket.created_by, msg='Failed on_delete SET_NULL')
        self.assertEqual(ticket.created_by_name, self.user.name)
        
        # check that user.name is stored after delete
        message = Message.objects.get(pk=message.pk)
        self.assertIsNone(message.author, msg='Failed on_delete SET_NULL')
        self.assertEqual(message.author_name, self.user.name)
