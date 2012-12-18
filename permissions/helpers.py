from django.forms.formsets import all_valid
from django.contrib.admin import helpers
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.util import unquote
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils.encoding import force_text


# Copy Pasta of django.contrib.admin.options.ModelAdmin methods adding extra
#            permission management.


csrf_protect_m = method_decorator(csrf_protect)


@csrf_protect_m
@transaction.commit_on_success
def add_view(self, request, form_url='', extra_context=None):
    "The 'add' admin view for this model."
    model = self.model
    opts = model._meta
    
    if not self.has_add_permission(request):
        raise PermissionDenied
    
    ModelForm = self.get_form(request)
    formsets = []
    inline_instances = self.get_inline_instances(request, None)
    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES)
        if form.is_valid():
            new_object = self.save_form(request, form, change=False)
            form_validated = True
            if not self.has_add_permission(request, new_object):
                raise PermissionDenied
        else:
            form_validated = False
            new_object = self.model()
        prefixes = {}
        for FormSet, inline in zip(self.get_formsets(request), inline_instances):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1 or not prefix:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = FormSet(data=request.POST, files=request.FILES,
                              instance=new_object,
                              save_as_new="_saveasnew" in request.POST,
                              prefix=prefix, queryset=inline.queryset(request))
            formsets.append(formset)
        if all_valid(formsets) and form_validated:
            self.save_model(request, new_object, form, False)
            self.save_related(request, form, formsets, False)
            self.log_addition(request, new_object)
            return self.response_add(request, new_object)
    else:
        # Prepare the dict of initial data from the request.
        # We have to special-case M2Ms as a list of comma-separated PKs.
        initial = dict(request.GET.items())
        for k in initial:
            try:
                f = opts.get_field(k)
            except models.FieldDoesNotExist:
                continue
            if isinstance(f, models.ManyToManyField):
                initial[k] = initial[k].split(",")
        form = ModelForm(initial=initial)
        prefixes = {}
        for FormSet, inline in zip(self.get_formsets(request), inline_instances):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1 or not prefix:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = FormSet(instance=self.model(), prefix=prefix,
                              queryset=inline.queryset(request))
            formsets.append(formset)
    
    adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
        self.get_prepopulated_fields(request),
        self.get_readonly_fields(request),
        model_admin=self)
    media = self.media + adminForm.media
    
    inline_admin_formsets = []
    for inline, formset in zip(inline_instances, formsets):
        fieldsets = list(inline.get_fieldsets(request))
        readonly = list(inline.get_readonly_fields(request))
        prepopulated = dict(inline.get_prepopulated_fields(request))
        inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
            fieldsets, prepopulated, readonly, model_admin=self)
        inline_admin_formsets.append(inline_admin_formset)
        media = media + inline_admin_formset.media
    
    context = {
        'title': _('Add %s') % force_text(opts.verbose_name),
        'adminform': adminForm,
        'is_popup': "_popup" in request.REQUEST,
        'media': media,
        'inline_admin_formsets': inline_admin_formsets,
        'errors': helpers.AdminErrorList(form, formsets),
        'app_label': opts.app_label,
    }
    context.update(extra_context or {})
    return self.render_change_form(request, context, form_url=form_url, add=True)



@csrf_protect_m
@transaction.commit_on_success
def change_view(self, request, object_id, form_url='', extra_context=None):
    "The 'change' admin view for this model."
    model = self.model
    opts = model._meta
    
    obj = self.get_object(request, unquote(object_id))
    
    if obj is None:
        raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_text(opts.verbose_name), 'key': escape(object_id)})
    
    if not (self.has_change_permission(request, obj) or self.has_view_permission(request, obj)):
        raise PermissionDenied
    
    if request.method == 'POST' and "_saveasnew" in request.POST:
        if not self.has_change_permission(request, obj):
            raise PermissionDenied
        return self.add_view(request, form_url=reverse('admin:%s_%s_add' %
                                (opts.app_label, opts.module_name),
                                current_app=self.admin_site.name))
    
    ModelForm = self.get_form(request, obj)
    formsets = []
    inline_instances = self.get_inline_instances(request, obj)
    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form_validated = True
            new_object = self.save_form(request, form, change=True)
        else:
            form_validated = False
            new_object = obj
        prefixes = {}
        for FormSet, inline in zip(self.get_formsets(request, new_object), inline_instances):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1 or not prefix:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = FormSet(request.POST, request.FILES,
                              instance=new_object, prefix=prefix,
                              queryset=inline.queryset(request))
            
            formsets.append(formset)
        
        if all_valid(formsets) and form_validated:
            self.save_model(request, new_object, form, True)
            self.save_related(request, form, formsets, True)
            change_message = self.construct_change_message(request, form, formsets)
            self.log_change(request, new_object, change_message)
            return self.response_change(request, new_object)
    
    else:
        form = ModelForm(instance=obj)
        prefixes = {}
        for FormSet, inline in zip(self.get_formsets(request, obj), inline_instances):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1 or not prefix:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = FormSet(instance=obj, prefix=prefix,
                              queryset=inline.queryset(request))
            formsets.append(formset)
    
    adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
        self.get_prepopulated_fields(request, obj),
        self.get_readonly_fields(request, obj),
        model_admin=self)
    media = self.media + adminForm.media
    
    inline_admin_formsets = []
    for inline, formset in zip(inline_instances, formsets):
        fieldsets = list(inline.get_fieldsets(request, obj))
        readonly = list(inline.get_readonly_fields(request, obj))
        prepopulated = dict(inline.get_prepopulated_fields(request, obj))
        inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
            fieldsets, prepopulated, readonly, model_admin=self)
        inline_admin_formsets.append(inline_admin_formset)
        media = media + inline_admin_formset.media
    
    action = 'Change' if self.has_change_permission(request, obj) else 'View'
    
    context = {
        'title': _('%s %s') % (action, force_text(opts.verbose_name)),
        'adminform': adminForm,
        'object_id': object_id,
        'original': obj,
        'is_popup': "_popup" in request.REQUEST,
        'media': media,
        'inline_admin_formsets': inline_admin_formsets,
        'errors': helpers.AdminErrorList(form, formsets),
        'app_label': opts.app_label,
    }
    context.update(extra_context or {})
    return self.render_change_form(request, context, change=True, obj=obj, form_url=form_url)


@csrf_protect_m
def changelist_view(self, request, extra_context=None):
    """
    The 'change list' admin view for this model.
    """
    from django.contrib.admin.views.main import ERROR_FLAG
    opts = self.model._meta
    app_label = opts.app_label
    
    if not self.has_view_permission(request, None):
        raise PermissionDenied
    
    list_display = self.get_list_display(request)
    list_display_links = self.get_list_display_links(request, list_display)
    list_filter = self.get_list_filter(request)
    
    # Check actions to see if any are available on this changelist
    actions = self.get_actions(request)
    if actions:
        # Add the action checkboxes if there are any actions available.
        list_display = ['action_checkbox'] +  list(list_display)
    
    ChangeList = self.get_changelist(request)
    try:
        cl = ChangeList(request, self.model, list_display,
            list_display_links, list_filter, self.date_hierarchy,
            self.search_fields, self.list_select_related,
            self.list_per_page, self.list_max_show_all, self.list_editable,
            self)
    except IncorrectLookupParameters:
        # Wacky lookup parameters were given, so redirect to the main
        # changelist page, without parameters, and pass an 'invalid=1'
        # parameter via the query string. If wacky parameters were given
        # and the 'invalid=1' parameter was already in the query string,
        # something is screwed up with the database, so display an error
        # page.
        if ERROR_FLAG in request.GET.keys():
            return SimpleTemplateResponse('admin/invalid_setup.html', {
                'title': _('Database error'),
            })
        return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')
    
    # If the request was POSTed, this might be a bulk action or a bulk
    # edit. Try to look up an action or confirmation first, but if this
    # isn't an action the POST will fall through to the bulk edit check,
    # below.
    action_failed = False
    selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
    
    # Actions with no confirmation
    if (actions and request.method == 'POST' and
            'index' in request.POST and '_save' not in request.POST):
        if selected:
            response = self.response_action(request, queryset=cl.get_query_set(request))
            if response:
                return response
            else:
                action_failed = True
        else:
            msg = _("Items must be selected in order to perform "
                    "actions on them. No items have been changed.")
            self.message_user(request, msg)
            action_failed = True
    
    # Actions with confirmation
    if (actions and request.method == 'POST' and
            helpers.ACTION_CHECKBOX_NAME in request.POST and
            'index' not in request.POST and '_save' not in request.POST):
        if selected:
            response = self.response_action(request, queryset=cl.get_query_set(request))
            if response:
                return response
            else:
                action_failed = True
    
    # If we're allowing changelist editing, we need to construct a formset
    # for the changelist given all the fields to be edited. Then we'll
    # use the formset to validate/process POSTed data.
    formset = cl.formset = None
    
    # Handle POSTed bulk-edit data.
    if (request.method == "POST" and cl.list_editable and
            '_save' in request.POST and not action_failed):
        FormSet = self.get_changelist_formset(request)
        formset = cl.formset = FormSet(request.POST, request.FILES, queryset=cl.result_list)
        if formset.is_valid():
            changecount = 0
            for form in formset.forms:
                if form.has_changed():
                    obj = self.save_form(request, form, change=True)
                    self.save_model(request, obj, form, change=True)
                    self.save_related(request, form, formsets=[], change=True)
                    change_msg = self.construct_change_message(request, form, None)
                    self.log_change(request, obj, change_msg)
                    changecount += 1
            
            if changecount:
                if changecount == 1:
                    name = force_text(opts.verbose_name)
                else:
                    name = force_text(opts.verbose_name_plural)
                msg = ungettext("%(count)s %(name)s was changed successfully.",
                                "%(count)s %(name)s were changed successfully.",
                                changecount) % {'count': changecount,
                                                'name': name,
                                                'obj': force_text(obj)}
                self.message_user(request, msg)

            return HttpResponseRedirect(request.get_full_path())

    # Handle GET -- construct a formset for display.
    elif cl.list_editable:
        FormSet = self.get_changelist_formset(request)
        formset = cl.formset = FormSet(queryset=cl.result_list)

    # Build the list of media to be used by the formset.
    if formset:
        media = self.media + formset.media
    else:
        media = self.media
    
    # Build the action form and populate it with available actions.
    if actions:
        action_form = self.action_form(auto_id=None)
        action_form.fields['action'].choices = self.get_action_choices(request)
    else:
        action_form = None
    
    selection_note_all = ungettext('%(total_count)s selected',
        'All %(total_count)s selected', cl.result_count)
    
    context = {
        'module_name': force_text(opts.verbose_name_plural),
        'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
        'selection_note_all': selection_note_all % {'total_count': cl.result_count},
        'title': cl.title,
        'is_popup': cl.is_popup,
        'cl': cl,
        'media': media,
        'has_add_permission': self.has_add_permission(request),
        'app_label': app_label,
        'action_form': action_form,
        'actions_on_top': self.actions_on_top,
        'actions_on_bottom': self.actions_on_bottom,
        'actions_selection_counter': self.actions_selection_counter,
    }
    context.update(extra_context or {})
    
    return TemplateResponse(request, self.change_list_template or [
        'admin/%s/%s/change_list.html' % (app_label, opts.object_name.lower()),
        'admin/%s/change_list.html' % app_label,
        'admin/change_list.html'
    ], context, current_app=self.admin_site.name)

