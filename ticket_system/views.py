import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from ticket_system import models
from ticket_system import forms

@login_required
def show_tickets(request):
    """
    Shows a list of tickets, with user permissions
    """
    ordering = request.GET.get('ordering', 'status')

    try:
        raw_creators = map(lambda a: a.users.all(), user.research_groups.all())
        raw_creators = [item for sublist in raw_creators for item in sublist]
        research_group_creators = list(set( raw_creators ))
    except:
        research_group_creators = [request.user]
    
    tickets = models.Ticket.objects.filter(
        creator__in = research_group_creators
        ).order_by(ordering)
    
    return render_to_response("tickets/show_tickets.html",
                              RequestContext(request,
                                             {
                                                 'tickets': tickets,
                                                 'ordering': ordering
                                                 }
                                             )
                              )

@login_required
def show_ticket(request, ticket_id):
    """
    Shows all information about a single ticket.
    It also manages new messages
    """
    try:
        raw_creators = map(lambda a: a.users.all(), user.research_groups.all())
        raw_creators = [item for sublist in raw_creators for item in sublist]
        research_group_creators = list(set( raw_creators ))
    except:
        research_group_creators = [request.user]
    
    ticket = models.Ticket.objects.get(
        creator__in = research_group_creators,
        id = ticket_id
        )

    if request.method == "POST":
        form = forms.MessageForm(request.POST)
        if form.is_valid():
            instance = form.save(commit = False)
            instance.ticket = ticket
            instance.author = request.user
            instance.save()
            return HttpResponseRedirect("/ticket_system/ticket/%s/" % ticket_id)
    else:
        form = forms.MessageForm()
    
    return render_to_response("tickets/show_ticket.html",
                              RequestContext(request,
                                             {
                                                 'ticket': ticket,
                                                 'form': form
                                                 }
                                             )
                              )
    

@login_required
def create_ticket(request):
    """
    Creates a ticket
    """
    if request.method == "POST":
        form = forms.TicketForm(request.POST)
        if form.is_valid():
            instance = form.save(commit = False)
            instance.creator = request.user
            instance.owner = None
            instance.status = "New"
            instance.creation_date = datetime.datetime.now()
            instance.save()
            return HttpResponseRedirect("/ticket_system/")
    else:
        form = forms.TicketForm()
    return render_to_response("tickets/create_ticket.html",
                              RequestContext(request,
                                             {
                                                 'form': form,
                                                 }
                                             )
                              )
