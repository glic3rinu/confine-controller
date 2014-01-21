from controller.admin.filters import MySimpleListFilter

from .models import Ticket


class MyTicketsListFilter(MySimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = 'Tickets'
    parameter_name = 'my_tickets'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'My Tickets'),
            ('False', 'All'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.involved_by(request.user)


class TicketStateListFilter(MySimpleListFilter):
    title = 'State'
    parameter_name = 'state'
    
    def lookups(self, request, model_admin):
        return (
            ('OPEN', "Open"),
            (Ticket.NEW, "New"),
            (Ticket.IN_PROGRESS, "In Progress"),
            (Ticket.RESOLVED, "Resolved"),
            (Ticket.FEEDBACK, "Feedback"),
            (Ticket.REJECTED, "Rejected"),
            (Ticket.CLOSED, "Closed"),
            ('False', 'All'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'OPEN':
            return queryset.exclude(state__in=[Ticket.CLOSED, Ticket.REJECTED])
        elif self.value() == 'False':
            return queryset
        return queryset.filter(state=self.value())
