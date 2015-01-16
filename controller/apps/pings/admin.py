from __future__ import absolute_import

import json

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import RedirectView

from controller.admin.utils import display_timesince, wrap_admin_view
from controller.core.serializers import DecimalJSONEncoder
from controller.utils.apps import is_installed
from permissions.admin import PermissionModelAdmin

from .models import Ping
from .settings import PING_INSTANCES
from .tasks import ping


STATES_COLORS = {
    'OFFLINE': 'red',
    'NODATA': 'purple',
    'ONLINE': 'green',
}


class PingAdmin(PermissionModelAdmin):
    list_display = (
        'content_object', 'packet_loss_percentage', 'min', 'avg', 'max', 'mdev',
        'date', 'date_since'
    )
    list_display_links = ('content_object',)
    fields = list_display
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = list_display
    sudo_actions = ['delete_selected']
    deletable_objects_excluded = True
    
    def packet_loss_percentage(self, instance):
        return "<span title='%s samples'>%s%%</span>" % (instance.samples,
            instance.packet_loss)
    packet_loss_percentage.short_description = 'Packet loss'
    packet_loss_percentage.admin_order_field = 'packet_loss'
    packet_loss_percentage.allow_tags = True
    
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
    
    def get_urls(self):
        urls = patterns("",
            url("^(?P<content_type_id>\d+)/(?P<object_id>\d+)/$",
                wrap_admin_view(self, self.changelist_view),
                name='pings_ping_list'),
            url("^ping/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$",
                wrap_admin_view(self, self.ping_view),
                name='pings_ping_ping'),
            url("^(?P<content_type_id>\d+)/(?P<object_id>\d+)/timeseries/$",
                wrap_admin_view(self, self.timeseries_view),
                name='pings_ping_timeseries'),
            # As raw list of pings has no view we should handle manually
            # for example redirecting to the admin index.
            url("^$",
                RedirectView.as_view(pattern_name='admin:index'),
                name='pings_ping_changelist'),
        )
        return urls
        # + super(PingAdmin, self).get_urls()
    
    def get_changelist(self, request, **kwargs):
        """ Filter changelist by object """
        from django.contrib.admin.views.main import ChangeList
        class ObjectChangeList(ChangeList):
            def get_queryset(self, *args, **kwargs):
                qs = super(ObjectChangeList, self).get_queryset(*args, **kwargs)
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
        if content_type_id:
            object_id = kwargs.get('object_id')
            args = (content_type_id, object_id)
            request.ping_list_args = (content_type_id, object_id)
            ct = get_object_or_404(ContentType, pk=content_type_id)
            related_model = ct.model_class()
            related_object = get_object_or_404(related_model, pk=object_id)
            instance = Ping.get_instance_settings(related_model)
            addr = instance.get('get_addr')(related_object)
            for __, __, __, field in instance.get('admin_classes'):
                obj = getattr(related_object, field, False)
                if obj:
                    break
            obj = obj or related_object
            context.update({
                'ping_url': reverse('admin:pings_ping_ping', args=args),
                'obj_opts': obj._meta,
                'obj': obj,
                'ip_addr': addr,
                'metrics_url': reverse('admin:pings_ping_timeseries', args=args),
                'has_change_permission': self.has_change_permission(request, obj=obj, view=False),
            })
            self.change_list_template = 'admin/pings/ping/ping_list.html'
        else:
            self.change_list_template = None
        return super(PingAdmin, self).changelist_view(request, extra_context=context)
    
    def ping_view(self, request, content_type_id, object_id):
        ct = get_object_or_404(ContentType, pk=content_type_id)
        model = "%s.%s" % (ct.app_label, ct.model)
        try:
            ping(model, ids=[object_id], lock=False)
        except AttributeError:
            raise Http404
        args = (content_type_id, object_id)
        return redirect(reverse('admin:pings_ping_list', args=args))
    
    def timeseries_view(self, request, content_type_id, object_id):
        pings = Ping.objects.filter(content_type=content_type_id, object_id=object_id)
        pings = pings.order_by('date').extra(select={'epoch': "EXTRACT(EPOCH FROM date)"})
        series = pings.values_list('epoch', 'packet_loss', 'avg', 'min', 'max')
        data = [ [int(str(d).split('.')[0] + '000'),w,x,y,z] for d,w,x,y,z in series ]
        return HttpResponse(json.dumps(data, cls=DecimalJSONEncoder), content_type="application/json")


admin.site.register(Ping, PingAdmin)


# Monkey-patch section

def make_colored_address(old_method, field='', filters={}):
    """
    factory function that integrates ping into related object addresses
    displaying the address in representative colors and providing a link to
    its related time series data
    """
    def colored_address(self, obj, old_method=old_method, field=field, filters=filters):
        addr = old_method(self, obj)
        for k,v in filters.items():
            if getattr(obj, k) != v:
                return addr
        obj = getattr(obj, field, obj)
        ct = ContentType.objects.get_for_model(type(obj))
        url = reverse('admin:pings_ping_list', args=(ct.pk, obj.pk))
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
