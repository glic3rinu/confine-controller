# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

import datetime
import hashlib

from user_management import models
from user_management import forms

from django.contrib.auth import logout
from django.contrib.auth import models as auth_models
from django.contrib.auth.decorators import login_required

def register_user(request):
    if request.method == 'POST':
        reg_form = forms.RegisterForm(request.POST)
        if reg_form.is_valid():
            c_data = reg_form.cleaned_data

            new_user = auth_models.User.objects.create_user(
                username = c_data['username'], 
                password = c_data['password'], 
                email = c_data['email'],
                )
            new_user.is_active = False
            new_user.save()
            raw_key = str(datetime.datetime.now()) + c_data['username'] + c_data['password']
            hashed_key = hashlib.sha256(raw_key).hexdigest()
            new_request = models.ActivationRequest(user_id = new_user.id, key = hashed_key)
            new_request.save()
            return render_to_response('registration/after_register.html')
    else:
        reg_form = forms.RegisterForm()
    return render_to_response('registration/register.html', 
                              RequestContext(request, {'form': reg_form}))


def logged_in(request):
    if not request.META.get('PATH_INFO') == u'/logged_in/':
        return HttpResponseRedirect(request.META.get('PATH_INFO'))
    else:
        return HttpResponseRedirect("/")

@login_required
def custom_logout(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required
def user_delete_request(request):
    """
    Put user as inactive and creates an user delete request object for admins
    """
    if request.method == "GET":
        delete_req = request.GET.get("delete", '')
        if delete_req == "yes":
            delete_request = models.DeleteRequest(user = request.user)
            delete_request.save()
            user = request.user
            user.is_active = False
            user.save()
            logout(request)
            return HttpResponseRedirect("/")
        elif delete_req == "no":
            return HttpResponseRedirect("/")
        
    return render_to_response('user/user_delete_request.html', 
                              RequestContext(request, {}))

@login_required
def user_profile(request):
    """
    Shows user profile and allows its update through a form
    """
    user = request.user
    if request.method == "POST":
        form = forms.UserForm(request.POST)
        if form.is_valid():
            c_data = form.cleaned_data
            user.first_name = c_data.get("first_name")
            user.last_name = c_data.get("last_name")
            user.save()
            profile = user.get_profile()
            profile.ssh_key = c_data.get("ssh_key")
            profile.save()
    else:
        form = forms.UserForm(initial = {'first_name': user.first_name,
                                         'last_name': user.last_name,
                                         'ssh_key': user.get_profile().ssh_key})
    return render_to_response('user/user_profile.html', 
                              RequestContext(request, {'form': form}))


def change_user_password(request):
    """
    Shows a form to change user password
    """
    user = request.user
    if request.method == "POST":
        form = forms.ChangePasswordForm(request.POST)
        if form.is_valid():
            c_data = form.cleaned_data
            user.set_password(c_data.get("password"))
            user.save()
    else:
        form = forms.ChangePasswordForm
    return render_to_response('user/change_user_password.html', 
                              RequestContext(request, {'form': form}))
