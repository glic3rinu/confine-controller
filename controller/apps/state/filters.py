from django.contrib.admin import SimpleListFilter

from .models import NodeState, SliverState


class NodeStateListFilter(SimpleListFilter):
    title = 'State'
    parameter_name = 'state'
    
    def lookups(self, request, model_admin):
        return NodeState.STATES
    
    def queryset(self, request, queryset):
        if self.value():
            pks = [state.pk for state in queryset.all() if state.current == self.value()]
            return queryset.filter(pk__in=pks)


class SliverStateListFilter(SimpleListFilter):
    title = 'State'
    parameter_name = 'state'
    
    def lookups(self, request, model_admin):
        return SliverState.STATES
    
    def queryset(self, request, queryset):
        if self.value():
            pks = [state.pk for state in queryset.all() if state.current == self.value()]
            return queryset.filter(pk__in=pks)
