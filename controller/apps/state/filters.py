from django.contrib.admin import SimpleListFilter

from .models import State
from .settings import STATE_NODE_SOFT_VERSION_NAME


class NodeStateListFilter(SimpleListFilter):
    title = 'Current state'
    parameter_name = 'state'
    
    def lookups(self, request, model_admin):
        return State.NODE_STATES
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state_set__value=self.value())


class SliverStateListFilter(NodeStateListFilter):
    def lookups(self, request, model_admin):
        return State.SLIVER_STATES


class FirmwareVersionListFilter(SimpleListFilter):
    title = 'Firmware ver'
    parameter_name = 'soft_version'
    
    def lookups(self, request, model_admin):
        values = model_admin.model.objects.values_list('soft_version__value', flat=True)
        values = values.exclude(soft_version__value__isnull=True).distinct()
        values = [ (value, STATE_NODE_SOFT_VERSION_NAME(value)) for value in values ]
        values.sort(key=lambda a: 'x'+a[1] if a[1].startswith('m') else a[1], reverse=True)
        values.append(('None', 'No data'))
        return values
    
    def queryset(self, request, queryset):
        if self.value() == 'None':
            return queryset.filter(soft_version__value__isnull=True)
        if self.value():
            return queryset.filter(soft_version__value=self.value())

