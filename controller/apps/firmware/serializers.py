from __future__ import absolute_import

from celery.result import AsyncResult
from rest_framework.reverse import reverse

from api import serializers

from .models import Build, Config


class FirmwareSerializer(serializers.Serializer):
    state = serializers.CharField(read_only=True)
    progress = serializers.SerializerMethodField('get_progress')
    next = serializers.SerializerMethodField('get_next')
    description = serializers.SerializerMethodField('get_description')
    content_message = serializers.SerializerMethodField('get_content_message')
    image_url = serializers.HyperlinkedFileField(source='image', read_only=True)
    
    def __init__(self, build, **kwargs):
        super(FirmwareSerializer, self).__init__(build, **kwargs)
        config = Config.objects.get()
        for f in config.files.active().optional():
            field_name = '%s_%d' % (f.path.split('/')[-1].replace('.', '_'), f.pk)
            setattr(build, field_name, False)
            self.fields["%s" % field_name] = serializers.BooleanField(required=False)
        if build.pk:
            self.result = AsyncResult(build.task_id).result or {}
    
    def get_progress(self, instance):
        return getattr(self, 'result', {}).get('progress', None)
    
    def get_next(self, instance):
        return getattr(self, 'result', {}).get('next', None)
    
    def get_description(self, instance):
        return getattr(self, 'result', {}).get('description', None)
    
    def get_content_message(self, instance):
        return instance.state_description
