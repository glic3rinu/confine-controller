from django.contrib.admin import SimpleListFilter

from .models import State


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
