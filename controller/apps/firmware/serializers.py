from __future__ import absolute_import

from controller.core.validators import validate_cert

from api import serializers
from nodes.models import Server, ServerApi
from nodes.settings import NODES_NODE_ARCHS
from tinc.models import TincHost

from .exceptions import BaseImageNotAvailable
from .models import BaseImage, Build, Config


class BaseImageSerializer(serializers.UriHyperlinkedModelSerializer):
    architectures = serializers.MultiSelectField(choices=NODES_NODE_ARCHS)
    
    class Meta:
        model = BaseImage
        exclude = ('config',)
    
    def validate(self, attrs):
        # Initialize config with singleton value
        attrs['config'] = Config.objects.get()
        return attrs


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



class NodeFirmwareConfigSerializer(serializers.Serializer):
    base_image_id = serializers.IntegerField(required=False)
    registry_base_uri = serializers.URLField(required=False)
    registry_cert = serializers.CharField(
        required=False, validators=[validate_cert]
    )
    tinc_default_gateway = serializers.CharField(required=False)
    
    def __init__(self, node, *args, **kwargs):
        super(NodeFirmwareConfigSerializer, self).__init__(*args, **kwargs)
        self.node = node
    
    def get_default_registry(self):
        main_server = Server.objects.get_default()
        dflt_api = main_server.api.filter(type=ServerApi.REGISTRY).first()
        if dflt_api is None:
            raise ServerApi.DoesNotExist("Doesn't exist default registry API.")
        return dflt_api
    
    def validate_tinc_default_gateway(self, attrs, source):
        value = attrs.get(source, None)
        choices = TincHost.objects.servers().values_list('name', flat=True)
        
        if value is not None and value not in choices:
            raise serializers.ValidationError(
                'Select a valid choice. "%s" is not one of the available '
                'choices.' % value
            )
        
        return attrs
    
    def validate_base_image_id(self, attrs, source):
        """
        Initialize default base image (if any).
        Check if provided base image ID exists and has compatible
        arch with the node.
        
        """
        value = attrs.get(source, None)
        config = Config.objects.get()
        base_img_qs = config.get_images(self.node)
        
        if not value:
            base_image = base_img_qs.order_by('-default').first()
            if base_image is None:
                raise serializers.ValidationError(
                    "No base image compatible with the architecture of this "
                    "node."
                )
            attrs[source] = base_image.pk
        
        else:
            try:
                base_image = base_img_qs.get(pk=value)
            except BaseImage.DoesNotExist as e:
                raise serializers.ValidationError(
                    "Invalid ID - object does not exist."
                )
        
        return attrs
    
    def validate(self, attrs):
        """
        Initialize registry defaults and check if certificate is
        provided for HTTPS base URIs.
        
        """
        base_uri = attrs.get('registry_base_uri', '')
        cert = attrs.get('registry_cert', '')
        
        if not base_uri:
            if cert:
                raise serializers.ValidationError(
                    {'registry_base_uri': ['this field is required.']}
                )
            
            # initialize registry defaults
            base_uri = self.get_default_registry().base_uri
            cert = self.get_default_registry().cert
            attrs['registry_base_uri'] = base_uri
            attrs['registry_cert'] = cert
        
        if base_uri.startswith('https://') and not cert:
            raise serializers.ValidationError("Certificate is required for HTTPS.")
        
        # serializer is valid - apply changes
        # FIXME(santiago): changes are applied even if fails plugins validation.
        # http://tomchristie.github.io/rest-framework-2-docs/api-guide/serializers#saving-object-state
        gw_name = attrs.get('tinc_default_gateway', None)
        if gw_name:
            default_gateway = TincHost.objects.get(name=gw_name)
            self.node.tinc.default_connect_to = default_gateway
            self.node.tinc.save()
        return attrs
