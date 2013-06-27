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
        return obj.created_by == user
    
    def delete(self, obj, cls, user):
        return self.change(obj, cls, user)


class MessagePermission(Permission):
    def view(self, obj, cls, user):
        if obj is None:
            return True
        if obj.visibility == Message.PUBLIC:
            return True
        elif obj.visibility == Message.PRIVATE:
            return obj.author == user
        elif obj.visibility == Message.INERNAL:
            return obj.ticket.group.is_member(user)
    
    def add(self, obj, cls, user):
        return True
    
    def change(self, obj, cls, user):
        if obj is None:
            return True
        return obj.author == user


Ticket.has_permission = TicketPermission()
Message.has_permission = MessagePermission()
