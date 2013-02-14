from controller.admin.filters import MySimpleListFilter


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
