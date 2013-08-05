from __future__ import absolute_import

from permissions import Permission

from .models import Ticket, Message


# FIXME this permissions are wrong, correct them

class TicketPermission(Permission):
    def view(self, obj, cls, user):
        return True
    
    def add(self, obj, cls, user):
        return True
    
    def change(self, obj, cls, user):
        if obj is None:
            return True
        return obj.is_involved_by(user)
    
    def delete(self, obj, cls, user):
        return self.change(obj, cls, user)


class MessagePermission(Permission):
    def view(self, obj, cls, user):
        return True
    
    def add(self, obj, cls, user):
        return True
    
    def change(self, obj, cls, user):
        if obj is None:
            return True
        return obj.author == user


Ticket.has_permission = TicketPermission()
Message.has_permission = MessagePermission()
