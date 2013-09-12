from django.contrib.admin import SimpleListFilter

from .models import State


class NodeStateListFilter(SimpleListFilter):
    title = 'Current state'
    parameter_name = 'state'
    
    def lookups(self, request, model_admin):
        return State.NODE_STATES
    
    def queryset(self, request, queryset):
        if self.value():
            pks = [node.pk for node in queryset.all() if node.state.current == self.value()]
            return queryset.filter(pk__in=pks)


class SliverStateListFilter(SimpleListFilter):
    title = 'Current state'
    parameter_name = 'state'
    
    def lookups(self, request, model_admin):
        return State.SLIVER_STATES
    
    def queryset(self, request, queryset):
        if self.value():
            pks = [sliver.pk for sliver in queryset.all() if sliver.state.current == self.value()]
            return queryset.filter(pk__in=pks)
