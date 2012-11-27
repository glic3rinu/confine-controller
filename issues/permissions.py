import inspect

from users.permissions import Permission

from .models import Ticket, Message


# FIXME this permissions are wrong, correct them

class TicketPermission(Permission):
    def view(self, caller, user):
        return True
    
    def change(self, caller, user):
        if inspect.isclass(caller):
            return True


class MessagePermission(Permission):
    def view(self, caller, user):
        if not inspect.isclass(caller):
            if caller.visibility == Message.PUBLIC:
                return True
            elif caller.visibility == Message.PRIVATE:
                return caller.author == user
            elif caller.visibility == Message.INERNAL:
                return caller.ticket.group in user.groups.all()
        return False


Ticket.has_permission = TicketPermission()
Message.has_permission = MessagePermission()
