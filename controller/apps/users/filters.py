from django.contrib.admin import SimpleListFilter


class MyGroupsListFilter(SimpleListFilter):
    """ Filter slices by group according to request.user """
    title = 'Groups'
    parameter_name = 'my_groups'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'My Groups'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(users=request.user)
