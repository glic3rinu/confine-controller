import os
import tempfile

from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_unicode


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
            # Dirty hack in order to allow pk values on sliver data filename
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
    """Mark as readonly if exists file for data."""
    readonly_fields = []
    for field in ['data',]:
        if bool(getattr(obj, field, False)): # False when obj is None
            readonly_fields += [field+'_uri', field+'_sha256']
    return readonly_fields


def log_sliver_history(user_id, object, msg):
    """Log sliver history on the node (debug purposes)"""
    LogEntry.objects.log_action(
        user_id         = user_id,
        content_type_id = ContentType.objects.get_for_model(object.node).pk,
        object_id       = object.node.pk,
        object_repr     = force_unicode(object.node),
        action_flag     = CHANGE,
        change_message  = msg
    )


@deconstructible
class UploadToGenerator(object):
    field_name = ''
    base_path = ''
    file_name = ''
    
    def __init__(self, field_name, base_path, file_name):
        self.field_name = field_name
        self.base_path = base_path
        self.file_name = file_name
    
    def __call__(self, instance, filename):
        if not self.file_name or instance is None:
            return os.path.join(self.base_path, filename)
        field = type(instance)._meta.get_field_by_name(self.field_name)[0]
        storage_location = field.storage.base_location
        abs_path = os.path.join(storage_location, self.base_path)
        splited = filename.split('.')
        context = {
            'pk': instance.pk,
            'original': filename,
            'prefix': splited[0],
            'suffix': splited[1] if len(splited) > 1 else ''
        }
        if '%(rand)s' in self.file_name:
            prefix, suffix = self.file_name.split('%(rand)s')
            prefix = prefix % context
            suffix = suffix % context
            with tempfile.NamedTemporaryFile(dir=abs_path, prefix=prefix, suffix=suffix) as f:
                name = f.name.split('/')[-1]
        else:
            name = self.file_name % context
        name = name.replace(' ', '_')
        return os.path.join(self.base_path, name)
    
    def __eq__(self, other):
        return (self.field_name == other.field_name and
                self.base_path == other.base_path and
                self.file_name == other.file_name)
