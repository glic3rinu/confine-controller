from django.conf.urls import patterns, url
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.encoding import force_unicode

from controller.admin.utils import wrap_admin_view


class SingletonModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        """ Singleton pattern: prevent addition of new objects """
        return False
        
    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = patterns('',
            url(r'^(?P<object_id>\d+)/history/$',
                wrap_admin_view(self, self.history_view),
                name='%s_%s_history' % info),
            url(r'^(?P<object_id>\d+)/delete/$',
                wrap_admin_view(self, self.delete_view),
                name='%s_%s_delete' % info),
            url(r'^(?P<object_id>\d+)$',
                wrap_admin_view(self, self.change_view),
                name='%s_%s_change' % info),
            url(r'^history/$',
                wrap_admin_view(self, self.history_view), {'object_id': '1'},
                name='%s_%s_history' % info),
            url(r'^delete/$',
                wrap_admin_view(self, self.delete_view), {'object_id': '1'},
                name='%s_%s_delete' % info),
            url(r'^$',
                wrap_admin_view(self, self.change_view), {'object_id': '1'},
                name='%s_%s_change' % info),
            url(r'^$',
                wrap_admin_view(self, self.change_view), {'object_id': '1'},
                name='%s_%s_changelist' % info),
        )
        return urlpatterns
        
    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        msg = '%(obj)s was changed successfully.' % {'obj': force_unicode(obj)}
        if request.POST.has_key("_continue"):
            self.message_user(request, msg + " You may edit it again below.")
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg)
            return HttpResponseRedirect("../../")
    
    def change_view(self, request, object_id, extra_context=None):
        if object_id=='1':
            self.model.objects.get_or_create(pk=1)
        return super(SingletonModelAdmin, self).change_view(request, object_id,
                extra_context=extra_context)

