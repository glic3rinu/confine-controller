import json
import six

from rest_framework import exceptions
from rest_framework.serializers import *

# Haking rest_framework in order to meet our crazy design specifications


class RelHyperlinkedRelatedField(HyperlinkedRelatedField):
    """ 
    HyperlinkedRelatedField field providing a relation object rather than flat URL 
    """
    def to_native(self, obj):
        # FIXME this doesn't work when posting
        url = super(RelHyperlinkedRelatedField, self).to_native(obj)
        if url is None:
             return None
        return {'uri': url}
    
    def from_native(self, value):
        # TODO this is bullshit, fixit!
        if isinstance(value, six.text_type):
            value = value.replace("u'", '"').replace("'", '"')
            value = json.loads(value)
        value = value.pop('uri')
        return super(RelHyperlinkedRelatedField, self).from_native(value)


class UriHyperlinkedModelSerializer(HyperlinkedModelSerializer):
    """ 
    Like HyperlinkedModelSerializer but renaming url field to uri 
    """
    uri = Field()
    _hyperlink_field_class = RelHyperlinkedRelatedField
    

    def __init__(self, *args, **kwargs):
        super(UriHyperlinkedModelSerializer, self).__init__(*args, **kwargs)
        self.fields['uri'] = self.fields.pop('url', None)
   

class HyperlinkedFileField(FileField):
    def to_native(self, value):
        if value:
            request = self.context.get('request')
            return request.build_absolute_uri(value.url)


class PropertyField(WritableField):
    """
    Dict-like representation of a Property Model
    A bit hacky, objects get deleted on from_native method and Serializer will
    need a custom override of restore_object method.
    """
    def to_native(self, value):
        """ Dict-like representation of a Property Model"""
        return dict((prop.name, prop.value) for prop in value.all())
    
    def from_native(self, value):
        """ Convert a dict-like representation back to a Property Model """
        parent = self.parent
        related_manager = getattr(parent.object, self.source or 'properties', False)
        properties = []
        if value:
            model = getattr(parent.opts.model, self.source or 'properties').related.model
            if isinstance(value, basestring):
                try:
                    value = json.loads(value)
                except:
                    raise exceptions.ParseError("Malformed property: %s" % str(value))
            if not related_manager:
                # POST (new parent object)
                return [ model(name=n, value=v) for n,v in value.iteritems() ]
            # PUT
            to_save = []
            for (name, value) in value.iteritems():
                try:
                    # Update existing property
                    prop = related_manager.get(name=name)
                except model.DoesNotExist:
                    # Create a new one
                    prop = model(name=name, value=value)
                else:
                    prop.value = value
                    to_save.append(prop.pk)
                properties.append(prop)
        
        # Discart old values
        if related_manager:
            for obj in related_manager.all():
                if obj.pk not in to_save:
                    # TODO do it in serializer.save()
                    obj.delete()
        return properties


class MultiSelectField(ChoiceField):
    def valid_value(self, value):
        for arch in value:
            valid = super(MultiSelectField, self).valid_value(arch)
            if not valid:
                return False
        return True
