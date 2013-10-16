from __future__ import absolute_import

from api import serializers

from .models import Config, Build


class FirmwareSerializer(serializers.Serializer):
    state = serializers.Field()
    progress = serializers.SerializerMethodField('get_progress')
    next = serializers.SerializerMethodField('get_next')
    description = serializers.SerializerMethodField('get_description')
    content_message = serializers.SerializerMethodField('get_content_message')
    image_url = serializers.HyperlinkedFileField(source='image', read_only=True)
    
    class Meta:
        model = Build
    
    def get_state(self, instance):
        if self.build:
            return self.build.state
        return 'non'
    
    def get_task_info(self, info):
        if self.object:
            task = self.object.task
            result = task.result or {}
            return result.get(info, None)
        return None
    
    def get_progress(self, instance):
        return self.get_task_info('progress')
    
    def get_next(self, instance):
        return self.get_task_info('next')
    
    def get_description(self, instance):
        if self.object:
            task = self.object.task
            result = task.result or {}
            description = result.get('description', 'Waiting for your build task to begin.')
            if self.get_progress(instance) == 100:
                return "Building process finished"
            return "%s ..." % description
        return ""
    
    def get_content_message(self, instance):
        if self.object:
            return self.object.state_description
        return ""
