from django.contrib import admin
from django.utils.functional import update_wrapper
from models import Node, NodeProp, Host, Gateway, Server, ResearchDevice, RdDirectIface
from singleton_models.admin import SingletonModelAdmin


class NodePropInline(admin.TabularInline):
    model = NodeProp
    extra = 0


class ResearchDeviceInline(admin.StackedInline):
    model = ResearchDevice
    max_num = 0


class NodeAdmin(admin.ModelAdmin):
    inlines = [ResearchDeviceInline, NodePropInline]


class ServerAdmin(SingletonModelAdmin):

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^history/$',
                wrap(self.history_view),
                {'object_id': '1'},
                name='%s_%s_history' % info),
            url(r'^$',
                wrap(self.change_view),
                {'object_id': '1'},
                name='%s_%s_change' % info),
            url(r'^$',
                wrap(self.change_view),
                {'object_id': '1'},
                name='%s_%s_changelist' % info),
        )
        return urlpatterns


admin.site.register(Node, NodeAdmin)
admin.site.register(Host)
admin.site.register(Gateway)
admin.site.register(Server, ServerAdmin)
admin.site.register(ResearchDevice)
