from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from controller.utils import is_installed

from .models import Ping
from .settings import PING_INSTANCES


STATES_COLORS = {
    'OFFLINE': 'red',
    'NODATA': 'purple',
    'ONLINE': 'green',}


class PingAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'packet_loss', 'min', 'avg', 'max', 'mdev', 'date')
    fields = list_display
    readonly_fields = list_display
    
    def has_add_permission(self, *args, **kwargs):
        return False


admin.site.register(Ping, PingAdmin)


# Monkey-patch section

def make_colored_address(old_method, field='', filters={}):
    def colored_address(self, obj, old_method=old_method, field=field, filters=filters):
        addr = old_method(self, obj)
        for k,v in filters.items():
            if getattr(obj, k) != v:
                return addr
        obj = getattr(obj, field, obj)
        ct = ContentType.objects.get_for_model(self.model)
        url = reverse('admin:ping_ping_changelist')
        url += '?content_type=%i&object_id=%i' % (ct.pk, obj.pk)
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
        for admin_class, field_name, field in instance.get('admin_classes'):
            context['admin'] = admin_class
            exec('from %(app)s.admin import %(admin)s as admin' % context)
            model_field = lambda self, obj: getattr(obj, field_name)
            model_field.short_description = field_name
            old_method = getattr(admin, field_name, model_field)
            filters = instance.get('filter', {})
            setattr(admin, field_name, make_colored_address(old_method, field=field, filters=filters))
