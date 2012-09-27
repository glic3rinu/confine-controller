from django.contrib import admin
from models import Ticket, Queue, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    
    
class TicketAdmin(admin.ModelAdmin):
    inline = [MessageInline]


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Queue)
