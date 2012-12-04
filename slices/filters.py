from django.contrib.admin import SimpleListFilter


class MySlicesListFilter(SimpleListFilter):
    """ Filter slices by group according to request.user """
    title = 'Slices'
    parameter_name = 'my_slices'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'My Slices'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(group__user=request.user)


class MySliversListFilter(SimpleListFilter):
    """ Filter slices by group according to request.user """
    title = 'Slivers'
    parameter_name = 'my_slivers'
    
    def lookups(self    , request, model_admin):
        return (
            ('True', 'My Slivers'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(slice_group__user=request.user)
