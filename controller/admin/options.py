from django.contrib import admin
from django.conf.urls import patterns, url

from controller.admin.utils import action_to_view


class AddOrChangeInlineForm(admin.options.InlineModelAdmin):
    """ 
        Inline class providing support for independent change and add inline forms
            add_form = AddSystemUserInlineForm
            change_form = ChangeSystemUserInlineForm
    """
    def get_formset(self, request, obj=None, **kwargs):
        # Determine if we need to use add_form or change_form
        field_name = self.model._meta.module_name
        try:
            getattr(obj, field_name)
        except (self.model.DoesNotExist, AttributeError):
            if hasattr(self, 'add_form'):
                self.form = self.add_form
        else:
            if hasattr(self, 'change_form'):
                self.form = self.change_form
        
        return super(AddOrChangeInlineFormMixin, self).get_formset(request, obj=obj, **kwargs)


class ChangeViewActionsModelAdmin(admin.options.ModelAdmin):
    """
        Make actions visible on the admin change view page.
        Note: If you want to provide a custom change form template then you should
            specify it with modeladmin.change_form_template = "your template"
        Usage 1:
            change_view_actions = [('reboot', reboot_view, 'Reboot', 'historylink'), 
                                 ('reboot', 'reboot_view', '', '')]
        Usage 2: 
            modeladmin.set_change_view_action('reboot', reboot_view, '', '')
    """
    def __init__(self, *args, **kwargs):
        super(ChangeViewActionsModelAdmin, self).__init__(*args, **kwargs)
        if not hasattr(self, 'change_view_actions'):
            self.change_view_actions = []
        else:
            links = [ self._prepare_change_view_action(*link) for link in self.change_view_actions ]
            self.change_view_actions = links
        if not self.change_form_template:
            self.change_form_template = "admin/controller/change_form.html"
    
    def get_urls(self):
        """Returns the additional urls for the change view links"""
        urls = super(ChangeViewActionsModelAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        new_urls = patterns("")
        for link in self.change_view_actions:
            new_urls += patterns("", url("^(?P<object_id>\d+)/%s/$" % link[0], admin_site.admin_view(link[1]), 
                name='%s_%s_%s' % (opts.app_label, opts.module_name, link[0])))
        return new_urls + urls
    
    def get_change_view_actions(self):
        return self.change_view_actions
    
    def set_change_view_action(self, name, view, description, css_class):
        self.change_view_actions.append(self._prepare_change_view_action(name, view, description, css_class))
    
    def _prepare_change_view_action(self, name, action, description, css_class):
        if isinstance(action, str) or isinstance(action, unicode):
            action = getattr(self, action)
        view = action_to_view(action, self)
        if description == '':
            description = name.capitalize()
        if css_class == '':
            css_class = 'historylink' 
        return (name, view, description, css_class)
    
    def change_view(self, *args, **kwargs):
        extra_context = kwargs['extra_context'] if 'extra_context' in kwargs else {}
        if extra_context is None:
            extra_context = {}
        extra_context.update({'object_tools_items': self.get_change_view_actions()})
        kwargs['extra_context'] = extra_context
        return super(ChangeViewActionsModelAdmin, self).change_view(*args, **kwargs)
