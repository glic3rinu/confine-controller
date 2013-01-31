"""
Views which allow users to create and activate accounts.

"""


from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from groupregistration.backends import get_backend

# TODO extend from registration.views import register
#       for avoid an authenticated user sign in again
#
#def register(request, backend, success_url=None, form_class=None,
#             disallowed_url='registration_disallowed',
#             template_name='registration/registration_form.html',
#             extra_context=None):
#    [...]
#    backend = get_backend(backend)
    # authenticated users cannot sign in again
#    if request.user.is_authenticated():
#        to, args, kwargs = backend.post_logged_redirect(request, request.user)
#        return redirect(to, *args, **kwargs)
#
#    [...]

def register_group(request, backend,
             template_name='registration_group_form.html'):

    if request.user.is_authenticated():
        return register_only_group(request, backend, template_name)

    backend = get_backend(backend)
    context = RequestContext(request)

    group_form_class = backend.group_get_form_class(request)
    user_form_class  = backend.get_form_class(request)
        
    if request.method == 'POST':
        group_form = group_form_class(data=request.POST, files=request.FILES)
        user_form = user_form_class(data=request.POST, files=request.FILES, prefix='user')

        if group_form.is_valid() and user_form.is_valid():
            # http://collingrady.wordpress.com/2008/02/18/editing-multiple-objects-in-django-with-newforms/
            # add prefix to user_form (avoid collisions group-user fields)
            for key in user_form.cleaned_data.keys():
                group_form.cleaned_data['user-'+key] = user_form.cleaned_data[key]

            new_group_reg = backend.group_register(request, **group_form.cleaned_data)

            to, args, kwargs = backend.group_post_registration_redirect(request, new_group_reg)
            return redirect(to, *args, **kwargs)

    else: #create empty form
        group_form = group_form_class()
        user_form = user_form_class(prefix='user')

    return render_to_response(template_name,
                              {'form': group_form,
                               'user_form': user_form},
                              context_instance=context)

def register_only_group(request, backend,
             template_name='registration_group_form.html'):

    if not request.user.is_authenticated():
        return register_group(request, backend, template_name)

    backend = get_backend(backend)
    context = RequestContext(request)

    form_class = backend.group_get_form_class(request)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)

        if form.is_valid():
            new_group_reg = backend.group_register(request, **form.cleaned_data)

            to, args, kwargs = backend.group_post_registration_redirect(request, new_group_reg)
            return redirect(to, *args, **kwargs)

    else: #create empty form
        form = form_class()

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=context)

