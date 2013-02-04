from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def wrap_action(action, modeladmin):
    def wrapper(request, object_id, slice_id, modeladmin=modeladmin, action=action):
        queryset = modeladmin.model.objects.filter(pk=object_id)
        response = action(modeladmin, request, queryset)
        if not response:
            opts = modeladmin.model._meta
            return HttpResponseRedirect(reverse('admin:slices_slice_slivers', 
                kwargs={'slice_id': slice_id, 'object_id': object_id}))
        return response
    return wrapper


def remove_slice_id(view):
    def wrapper(*args, **kwargs):
        kwargs.pop('slice_id')
        return view(*args, **kwargs)
    return wrapper

