from __future__ import absolute_import

from django.contrib.admin import options, actions
from django.contrib.admin.helpers import AdminReadonlyField
from django.contrib.admin.util import NestedObjects, quote
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.text import capfirst


# Monkey-patch get_deleted_objects in order to hide deletable_objects_excluded = True
def get_deleted_objects(objs, opts, user, admin_site, using):
    collector = NestedObjects(using=using)
    collector.collect(objs)
    perms_needed = set()
    
    def clean_empty(objects):
        cleaned = []
        for obj in objects:
            if isinstance(obj, list):
                cleaned.append(clean_empty(obj))
            elif obj != '':
                cleaned.append(obj)
        return cleaned if cleaned else '"Hidden objects"'
    
    def format_callback(obj):
        has_admin = admin_site._registry.get(obj.__class__, False)
        opts = obj._meta
        if has_admin:
            if getattr(has_admin, 'deletable_objects_excluded', False):
                return ''
            admin_url = reverse('%s:%s_%s_change'
                                % (admin_site.name,
                                   opts.app_label,
                                   opts.object_name.lower()),
                                None, (quote(obj._get_pk_val()),))
            p = '%s.%s' % (opts.app_label,
                           opts.get_delete_permission())
            if not user.has_perm(p):
                perms_needed.add(opts.verbose_name)
            # Display a link to the admin page.
            # NOTE: Define as unicode for avoid errors when obj
            # representation contains non-ascii chars
            return format_html(u'{0}: <a href="{1}">{2}</a>',
                               capfirst(opts.verbose_name),
                               admin_url,
                               obj)
        else:
            # Don't display link to edit, because it either has no
            # admin or is edited inline.
            return u'%s: %s' % (capfirst(opts.verbose_name),
                                force_text(obj))
    to_delete = collector.nested(format_callback)
    to_delete = clean_empty(to_delete)
    protected = [format_callback(obj) for obj in collector.protected]
    return to_delete, perms_needed, protected
options.get_deleted_objects = get_deleted_objects
actions.get_deleted_objects = get_deleted_objects


from controller.admin.options import *

# Monkey-patch AdminReadonlyField in order to support help_text deffinitions
old_init = AdminReadonlyField.__init__
def __init__(self, form, field, is_first, model_admin=None):
    old_init(self, form, field, is_first, model_admin=model_admin)
    if not self.field['help_text'] and not callable(field):
        method = getattr(model_admin, field, None)
        self.field['help_text'] = getattr(method, 'help_text', '')
AdminReadonlyField.__init__ = __init__


# Testbed admin class
from controller.models import Testbed, TestbedParams
from controller.utils.singletons.admin import SingletonModelAdmin
from permissions.admin import PermissionModelAdmin, PermissionTabularInline

class TestbedParamsInline(PermissionTabularInline):
    model = TestbedParams

class TestbedAdmin(SingletonModelAdmin, PermissionModelAdmin):
    model = Testbed
    inlines = [TestbedParamsInline]

    def has_delete_permission(self, *args, **kwargs):
        """ It doesn't make sense to delete the testbed """
        return False

admin.site.register(Testbed, TestbedAdmin)
