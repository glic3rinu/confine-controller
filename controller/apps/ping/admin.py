from __future__ import absolute_import

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.safestring import mark_safe

from controller.admin.utils import display_timesince
from controller.utils import is_installed
from permissions.admin import PermissionModelAdmin

from .models import Ping
from .settings import PING_INSTANCES
from .tasks import ping


STATES_COLORS = {
    'OFFLINE': 'red',
    'NODATA': 'purple',
    'ONLINE': 'green',}


class PingAdmin(PermissionModelAdmin):
    list_display = ('content_object', 'packet_loss', 'min', 'avg', 'max', 'mdev', 'date_since')
    fields = list_display
    list_display_links = ('content_object',)
    readonly_fields = list_display
    sudo_actions = ['delete_selected']
    
    def date_since(self, instance):
        return display_timesince(instance.date)
    date_since.admin_order_field = 'date'
    
    def get_list_display(self, request):
        list_display = super(PingAdmin, self).get_list_display(request)
        if hasattr(request, 'ping_list_args'):
            return list_display[1:]
        return list_display
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def get_actions(self, request):
        """ Exclude manage tickets actions for NOT superusers """
        actions = super(PingAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            for action in self.sudo_actions:
                if action in actions:
                    del actions[action]
        return actions
    
    def get_urls(self):
        urls = patterns("",
            url("^(?P<content_type_id>\d+)/(?P<object_id>\d+)/",
                self.changelist_view,
                name='ping_ping_list'),
            url("^ping/(?P<content_type_id>\d+)/(?P<object_id>\d+)/",
                self.ping_view,
                name='ping_ping_ping')
        )
        return urls + super(PingAdmin, self).get_urls()
    
    def get_changelist(self, request, **kwargs):
        """ Filter changelist by object """
        from django.contrib.admin.views.main import ChangeList
        class ObjectChangeList(ChangeList):
            def get_query_set(self, *args, **kwargs):
                qs = super(ObjectChangeList, self).get_query_set(*args, **kwargs)
                if hasattr(request, 'ping_list_args'):
                    content_type, object_id = request.ping_list_args
                    return qs.filter(content_type=content_type, object_id=object_id)
                return qs
        return ObjectChangeList
    
    def changelist_view(self, request, *args, **kwargs):
        """ Provide ping action """
        context = kwargs.get('extra_context', {})
        context.update({
            'title': 'Pings'})
        content_type_id = kwargs.get('content_type_id', False)
        # TODO 404
        if content_type_id:
            object_id = kwargs.get('object_id')
            args = (content_type_id, object_id)
            request.ping_list_args = (content_type_id, object_id)
            # For the breadcrumbs ...
            ct = ContentType.objects.get_for_id(content_type_id)
            # FIXME: when this does not exists what to do?
            ping_object = Ping.objects.filter(
                content_type=content_type_id,
                object_id=object_id)[0]
            content_object = ping_object.content_object
            instance = Ping.get_instance_settings(ct.model_class())
            addr = instance.get('get_addr')(content_object)
            for __, __, __, field in instance.get('admin_classes'):
                obj = getattr(content_object, field, False)
                if obj:
                    break
            obj = obj or content_object
            context.update({
                'ping_url': reverse('admin:ping_ping_ping', args=args),
                'obj_opts': obj._meta,
                'obj': obj,
                'ip_addr': addr,
                'has_change_permission': self.has_change_permission(request, obj=ping_object, view=False),})
            self.change_list_template = 'admin/ping/ping/ping_list.html'
        else:
            self.change_list_template = None
        return super(PingAdmin, self).changelist_view(request, extra_context=context)
    
    def ping_view(self, request, content_type_id, object_id):
        ct = ContentType.objects.get_for_id(content_type_id)
        model = "%s.%s" % (ct.app_label, ct.model)
        ping(model, ids=[object_id], lock=False)
        args = (content_type_id, object_id)
        return redirect(reverse('admin:ping_ping_list', args=args))


admin.site.register(Ping, PingAdmin)


# Monkey-patch section

def make_colored_address(old_method, field='', filters={}):
    def colored_address(self, obj, old_method=old_method, field=field, filters=filters):
        addr = old_method(self, obj)
        for k,v in filters.items():
            if getattr(obj, k) != v:
                return addr
        obj = getattr(obj, field, obj)
        ct = ContentType.objects.get_for_model(type(obj))
        url = reverse('admin:ping_ping_list', args=(ct.pk, obj.pk))
        state = Ping.get_state(obj)
        color = STATES_COLORS.get(state, "black")
        context = {
            'color': color,
            'title': state,
            'url': url,
            'addr': addr }
        colored = '<b><a style="color: %(color)s;" title="%(title)s" href="%(url)s">%(addr)s</a></b>' % context
        return mark_safe(colored)
    colored_address.short_description = getattr(old_method, 'short_description', old_method.__name__)
    return colored_address


for instance in PING_INSTANCES:
    if is_installed(instance.get('app')):
        context = {'app': instance.get('app')}
        for admin_class, field_name, field, __ in instance.get('admin_classes'):
            context['admin'] = admin_class
            exec('from %(app)s.admin import %(admin)s as admin' % context)
            model_field = lambda self, obj: getattr(obj, field_name)
            model_field.short_description = field_name
            old_method = getattr(admin, field_name, model_field)
            filters = instance.get('filter', {})
            setattr(admin, field_name, make_colored_address(old_method, field=field, filters=filters))
