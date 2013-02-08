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


class MessagePermission(Permission):
    def view(self, caller, user):
        if not self._is_class(caller):
            if caller.visibility == Message.PUBLIC:
                return True
            elif caller.visibility == Message.PRIVATE:
                return caller.author == user
            elif caller.visibility == Message.INERNAL:
                return caller.ticket.group in user.groups.all()
        return False
    
    def add(self, caller, user):
        return True


Ticket.has_permission = TicketPermission()
Message.has_permission = MessagePermission()
