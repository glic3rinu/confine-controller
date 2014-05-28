from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def wrap_action(action, modeladmin):
    def wrapper(request, object_id, slice_id, modeladmin=modeladmin, action=action):
        queryset = modeladmin.model.objects.filter(pk=object_id)
        response = action(modeladmin, request, queryset)
        if not response:
            return HttpResponseRedirect(reverse('admin:slices_slice_slivers', 
                kwargs={'slice_id': slice_id, 'object_id': object_id}))
        return response
    return wrapper


def remove_slice_id(view):
    def wrapper(*args, **kwargs):
        kwargs.pop('slice_id')
        return view(*args, **kwargs)
    return wrapper


def save_files_with_pk_value(obj, fields, *args, **kwargs):
    for field in fields:
        if getattr(obj, field):
            # Dirty hack in order to allow pk values on exp_data filename
            field_value = getattr(obj, field)
            setattr(obj, field, None)
            super(type(obj), obj).save(*args, **kwargs)
            setattr(obj, field, field_value)


def state_value(state):
    """ Return a numeric value for Slice.STATES (comparation purposes) """
    from .models import Slice # avoid circular imports
    STATE_VALUES = dict((state[0], index) for index, state in enumerate(Slice.STATES))
    if state is None:
        return -1
    return STATE_VALUES.get(state)


def get_readonly_file_fields(obj):
    """Mark as readonly if exists file for exp_data and overlay"""
    readonly_fields = []
    for field in ['exp_data', 'overlay']:
        if bool(getattr(obj, field, False)): # False when obj is None
            readonly_fields += [field+'_uri', field+'_sha256']
    return readonly_fields
