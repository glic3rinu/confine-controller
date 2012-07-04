from django.conf.urls import patterns, include, url
from ticket_system import views

urlpatterns = patterns('',
                       url(r'^$',
                           views.show_tickets,
                           name="show_tickets"),
                       url(r'^ticket/([0-9]+)/$',
                           views.show_ticket,
                           name="show_ticket"),
                       url(r'^create_ticket/$',
                           views.create_ticket,
                           name="create_ticket"),
                       )
