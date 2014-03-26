from __future__ import absolute_import

from api import serializers

from .models import Config, Build


class FirmwareSerializer(serializers.ModelSerializer):
    state = serializers.Field()
    progress = serializers.SerializerMethodField('get_progress')
    next = serializers.SerializerMethodField('get_next')
    description = serializers.SerializerMethodField('get_description')
    content_message = serializers.SerializerMethodField('get_content_message')
    image_url = serializers.HyperlinkedFileField(source='image', read_only=True)
    
    class Meta:
        model = Build
        fields = (
            'state', 'progress', 'next', 'description', 'content_message', 'image_url', 'date'
        )
    
    def get_state(self, instance):
        if self.build:
            return self.build.state
        return None
    
    def get_task_info(self, info):
        if self.object:
            task = self.object.task
            result = task.result or {}
            try:
                return result.get(info, None)
            except AttributeError: # result is an error or exception
                return result
        return None
    
    def get_progress(self, instance):
        return self.get_task_info('progress')
    
    def get_next(self, instance):
        return self.get_task_info('next')
    
    def get_description(self, instance):
        # TODO move to model ?
        if self.object:
            task = self.object.task
            result = task.result or {}
            if self.get_progress(instance) == 100:
                return "Building process finished"
            try:
                return "%s ..." % result.get('description', 'Waiting for your building task to begin.')
            except AttributeError: # result is an error or exception
                return result
        return ""
    
    def get_content_message(self, instance):
        if self.object:
            return self.object.state_description
        return ""
