from django.contrib.admin import SimpleListFilter
from django.utils.encoding import force_text


class MySlicesListFilter(SimpleListFilter):
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
            return queryset.filter(group__user=request.user)
    
    def choices(self, cl):
        """ Enable default selection different than All """
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


class MySliversListFilter(SimpleListFilter):
    """ Filter slices by group according to request.user """
    title = 'Slivers'
    parameter_name = 'my_slivers'
    
    def lookups(self    , request, model_admin):
        return (
            ('True', 'My Slivers'),
            ('False', 'All'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(slice__group__user=request.user)
    
    def choices(self, cl):
        """ Enable default selection different than All """
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

