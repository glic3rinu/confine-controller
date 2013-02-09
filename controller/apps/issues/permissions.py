from __future__ import absolute_import

from permissions import Permission

from .models import Ticket, Message


# FIXME this permissions are wrong, correct them

class TicketPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        return True
    
    def change(self, caller, user):
        if self._is_class(caller):
            return True
        return caller.created_by == user
    
    def delete(self, caller, user):
        return self.change(caller, user)


class MessagePermission(Permission):
    def view(self, caller, user):
        if self._is_class(caller):
            return True
        if caller.visibility == Message.PUBLIC:
            return True
        elif caller.visibility == Message.PRIVATE:
            return caller.author == user
        elif caller.visibility == Message.INERNAL:
            return caller.ticket.group.is_member(user)
    
    def add(self, caller, user):
        return True
    
    def change(self, caller, user):
        if self._is_class(caller):
            return True
        return caller.author == user

Ticket.has_permission = TicketPermission()
Message.has_permission = MessagePermission()
