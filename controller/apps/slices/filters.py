from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from controller.admin.filters import MySimpleListFilter

from .models import Slice


class MySlicesListFilter(MySimpleListFilter):
    """ Filter slices by group according to request.user """
    title = 'Slices'
    parameter_name = 'my_slices'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'My Slices'),
            ('False', 'All'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(group__users=request.user)


class MySliversListFilter(MySimpleListFilter):
    """ Filter slices by group according to request.user """
    title = 'Slivers'
    parameter_name = 'my_slivers'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'My Slivers'),
            ('False', 'All'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(slice__group__users=request.user)


class SliverSetStateListFilter(SimpleListFilter):
    """ Filter sliver by their set_state (it can depend on the slice state) """
    title = 'Set State'
    parameter_name = 'set_state'
    
    def lookups(self, request, model_admin):
        return Slice.STATES
    
    def queryset(self, request, queryset):
        state = self.value()
        if state:
            # TODO use sliver.effective_state ?
            return queryset.filter(Q(set_state=state)|
                Q(set_state__isnull=True, slice__set_state=state))

