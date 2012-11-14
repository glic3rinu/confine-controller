from django.conf import settings as project_settings
from django.contrib import admin
from django.contrib.contenttypes import generic

from common.admin import insert_inline, insert_list_display, link
from nodes.models import Server, Node
from .models import CnHost


class CnHostInline(generic.GenericTabularInline):
    model = CnHost
    max_num = 1
    fields = ['app_url', 'cndb_uri', 'cndb_cached']
    readonly_fields = ['cndb_cached']
    verbose_name_plural = 'Community Host'
    can_delete = False
     
    def cndb_cached(self, instance):
        date = instance.cndb_cached_on
        if not date: return 'Never'
        return date
    cndb_cached.short_description=CnHost._meta.get_field_by_name('cndb_cached_on')[0].verbose_name


# Monkey-Patching Section

app_url_link = link('cn__app_url', description='CN URL')

insert_inline(Node, CnHostInline)
insert_inline(Server, CnHostInline)
insert_list_display(Node, app_url_link)

if 'tinc' in project_settings.INSTALLED_APPS:
    from tinc.models import Gateway
    insert_inline(Gateway, CnHostInline)
    insert_list_display(Gateway, app_url_link)
