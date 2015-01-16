from django.contrib import admin
from django.conf.urls import patterns, url

from controller.admin.utils import action_to_view, set_default_filter
from controller.utils.singletons.admin import SingletonModelAdmin

from .helpers import FuncAttrWrapper, SortableField


class AddOrChangeInlineForm(admin.options.InlineModelAdmin):
    """
    Inline class providing support for independent change and add inline forms
        add_form = AddSystemUserInlineForm
        change_form = ChangeSystemUserInlineForm
    """
    def get_formset(self, request, obj=None, **kwargs):
        # Determine if we need to use add_form or change_form
        field_name = self.model._meta.model_name
        try:
            getattr(obj, field_name)
        except (self.model.DoesNotExist, AttributeError):
            if hasattr(self, 'add_form'):
                self.form = self.add_form
        else:
            if hasattr(self, 'change_form'):
                self.form = self.change_form
        return super(AddOrChangeInlineForm, self).get_formset(request, obj=obj, **kwargs)


class ChangeViewActions(admin.options.ModelAdmin):
    """
    Make actions visible on the admin change view page.
    Note: If you want to provide a custom change form template then you should
        specify it with modeladmin.change_form_template = "your template"
    Usage 1:
        change_view_actions = [reboot_view, 'request_certificate']
    Usage 2: 
        modeladmin.set_change_view_action(reboot_view)
    """
    def __init__(self, *args, **kwargs):
        super(ChangeViewActions, self).__init__(*args, **kwargs)
        if not hasattr(self, 'change_view_actions'):
            self.change_view_actions = []
        else:
            actions = self.change_view_actions
            views = [self._prepare_change_view_action(action) for action in actions]
            self.change_view_actions = views
        if not self.change_form_template:
            self.change_form_template = "admin/controller/change_form.html"
    
    def get_urls(self):
        """Returns the additional urls for the change view links"""
        urls = super(ChangeViewActions, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        new_urls = patterns("")
        for action in self.change_view_actions:
            singleton = SingletonModelAdmin in type(self).__mro__
            pattern = '^%s/$' if singleton else '^(\d+)/%s/$'
            new_urls += patterns("",
                url(pattern % action.url_name,
                    admin_site.admin_view(action),
                    name='%s_%s_%s' % (opts.app_label, opts.model_name, action.url_name)))
        return new_urls + urls
    
    def _prepare_change_view_action(self, action):
        if isinstance(action, str) or isinstance(action, unicode):
            action = getattr(self, action)
        view = action_to_view(action, self)
        view.url_name = getattr(action, 'url_name', action.__name__)
        view.verbose_name = getattr(action, 'verbose_name', view.url_name.capitalize())
        view.css_class = getattr(action, 'css_class', 'historylink')
        view.description = getattr(action, 'description', '')
        view.always_display = getattr(action, 'always_display', False)
        return view
    
    def get_change_view_actions_as_class(self):
        return [ FuncAttrWrapper(action) for action in self.change_view_actions ]
    
    def set_change_view_action(self, action):
        self.change_view_actions.append(self._prepare_change_view_action(action))
    
    def change_view(self, *args, **kwargs):
        extra_context = kwargs['extra_context'] if 'extra_context' in kwargs else {}
        if extra_context is None:
            extra_context = {}
        extra_context.update({'object_tools_items': self.get_change_view_actions_as_class()})
        kwargs['extra_context'] = extra_context
        return super(ChangeViewActions, self).change_view(*args, **kwargs)


class ChangeListDefaultFilter(object):
    """
    Enables support for default filtering on admin change list pages
    Your model admin class should define an default_changelist_filters attribute
    default_changelist_filters = (('my_nodes', 'True'),)
    """
    default_changelist_filters = ()
    
    def changelist_view(self, request, extra_context=None):
        """ Default filter as 'my_nodes=True' """
        defaults = []
        for queryarg, value in self.default_changelist_filters:
             set_default_filter(queryarg, request, value)
             defaults.append(queryarg)
        # hack response cl context in order to hook default filter awaearness into search_form.html template
        response = super(ChangeListDefaultFilter, self).changelist_view(request, extra_context=extra_context)
        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            response.context_data['cl'].default_changelist_filters = defaults
        return response


class SortableTabularInline(admin.options.TabularInline):
    """ 
        Inline that provides sortable functionallity
        Supports field override for related object attribute sort
        e.g. sortable_fields = {'node': 'node__name'} should replace
        sort by node id with sort by node name.
        Example usage:
        class SliverInline(PermissionTabularInline, SortableTabularInline):
            sortable_fields = {'node_link':'node__name'}
    """
    template = "admin/controller/edit_inline/tabular.html"
    sortable_fields = {} # optional field that allows override sorting
    
    def get_ordering(self, request):
        """ Define dynamic ordering based on request parameters """
        sortable_fields = self.get_sortable_fields(request)
        ordering = request.GET.get('o')
        try:
            # check user input
            column = abs(int(ordering))
            current_sfield = sortable_fields[column]
        except (IndexError, TypeError, ValueError):
            return self.ordering # default ordering or None
        
        current_sfield.update(ordering)
        sort_by = current_sfield.sort_by()
        # TODO: how to insert as extra_context and avoid using session??
        sfields_serialized = [x.serialize() for x in sortable_fields]
        request.session['sortable_fields'] = sfields_serialized
        return [sort_by]
    
    def get_sortable_fields(self, request):
        """ 
            Hack for get the inline fields SHOWED at admin page 
            NOTE: excludes primary key and hidden foreign key
            Returns SortableFields list
        """
        sortable_fields = []
    
        if self.fields:
            # generated admin fields cannot be selected as sort column
            for field in self.fields:
                sortable = field in self.model._meta.fields
                sortable_field = SortableField(field, len(sortable_fields), sortable)
                # insert overrides
                if field in self.sortable_fields:
                    sortable_field.name = self.sortable_fields.get(field)
                    sortable_field.sortable = True
                sortable_fields.append(sortable_field)
            return sortable_fields
        
        for field in self.model._meta.fields:
            if field.get_internal_type() == "ForeignKey":
                if field.rel.to is self.parent_model:
                    continue
            elif field.get_internal_type() == "AutoField":
                continue
            sortable_field = SortableField(field.name, len(sortable_fields))
            # insert overrides
            sortable_field.name = self.sortable_fields.get(field.name, field.name)
            sortable_fields.append(sortable_field)
        
        return sortable_fields

