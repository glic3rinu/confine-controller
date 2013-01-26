import ast

from rest_framework import serializers

# Haking rest_framework in order to meet our crazy design specifications


class RelHyperlinkedRelatedField(serializers.HyperlinkedRelatedField):
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
        value = ast.literal_eval(value).pop('uri')
        return super(RelHyperlinkedRelatedField, self).from_native(value)


class RelManyHyperlinkedRelatedField(serializers.ManyRelatedMixin, RelHyperlinkedRelatedField):
    """
    Represents a to-many relationship, using hyperlinking inside a relation object
    """
    pass


class UriHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    """ 
    Like HyperlinkedModelSerializer but renaming url field to uri 
    """
    uri = serializers.HyperlinkedIdentityField()
    
    def __init__(self, *args, **kwargs):
        super(UriHyperlinkedModelSerializer, self).__init__(*args, **kwargs)
        self.fields.pop('url')
    
    def get_related_field(self, model_field, to_many):
        """
        same as DRF2 but rturning RelXxxxXxxx
        """
        rel = model_field.rel.to
        kwargs = {
            'null': model_field.null,
            'queryset': rel._default_manager,
            'view_name': self._get_default_view_name(rel)
        }
        if to_many:
            return RelManyHyperlinkedRelatedField(**kwargs)
        return RelHyperlinkedRelatedField(**kwargs)


class HyperlinkedFileField(serializers.FileField):
    def to_native(self, value):
        if value:
            request = self.context.get('request', None)
            return request.build_absolute_uri(value.url)


