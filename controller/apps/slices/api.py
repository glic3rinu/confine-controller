from __future__ import absolute_import

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import Slice, Sliver, Template
from .serializers import (SliceSerializer, SliceCreateSerializer,
    SliverSerializer, SliverDetailSerializer, TemplateSerializer)


class Renew(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/server/do-renew`](
        http://confine-project.eu/rel/server/do-renew)
    
    Contains the function URI used to renew this slice.
    
    POST data: `null`
    """
    url_name = 'renew'
    rel = 'http://confine-project.eu/rel/server/do-renew'
    
    def post(self, request, *args, **kwargs):
        if not request.DATA:
            slice = get_object_or_404(Slice, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, slice)
            slice.renew()
            response_data = {'detail': 'Slice renewed for 30 days'}
            return Response(response_data, status=status.HTTP_200_OK)
        raise exceptions.ParseError(detail='This endpoint only accepts null data')


class Reset(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/server/do-reset`](
    http://confine-project.eu/rel/server/do-reset)
    
    Contains the function URI used to reset this slice.
    
    POST data: `null`
    """
    url_name = 'reset'
    rel = 'http://confine-project.eu/rel/server/do-reset'
    
    def post(self, request, *args, **kwargs):
        if not request.DATA:
            slice = get_object_or_404(Slice, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, slice)
            slice.reset()
            response_data = {'detail': 'Slice instructed to reset'}
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        raise exceptions.ParseError(detail='This endpoint only accepts null data')


def make_upload_file(model, field, field_url):
    # Just for the browsabe API
    attrs = {field: serializers.FileField()}
    UploadFlieSerializer = type(field+'Serializer', (serializers.Serializer,), attrs)
    
    # TODO ApiPermissionsMixin
    class UploadFile(generics.CreateAPIView):
        """
        **Relation type:** [`http://confine-project.eu/rel/controller/do-upload-%(field_url)s`](
            http://confine-project.eu/rel/controller/do-upload-%(field_url)s)
        
        Contains the function URI used to upload this resource's %(field)s file
        to some remote storage. The URI of the stored file will be placed in the
        `%(field)s_uri` member and its hash in `%(field)s_sha256`.
        
        POST data: `the contents of the file`
        
        Example: `curl -X POST -F "%(field)s=@%(field)s.tgz" ...`
        """ % {'field': field, 'field_url': field_url}
        url_name = 'upload-%s' % field_url
        rel = 'http://confine-project.eu/rel/controller/do-%s' % url_name
        serializer_class = UploadFlieSerializer
        
        def post(self, request, *args, **kwargs):
            obj = get_object_or_404(model, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, obj)
            if request.FILES:
                if len(request.FILES) > 1:
                    raise exceptions.ParseError(detail='Multiple files is not supported')
                uploaded_file = request.FILES.get(request.FILES.keys()[0])
            else:
                msg = "Only multipart/form-data is supported"
                raise exceptions.ParseError(detail=msg)
            # TODO move this validation logic elsewhere
            for validator in model._meta.get_field_by_name(field)[0].validators:
                try:
                    validator(uploaded_file)
                except ValidationError as e:
                    raise exceptions.ParseError(detail=str(e))
            getattr(obj, field).save(uploaded_file.name, uploaded_file)
            setattr(obj, field+'_uri', getattr(obj, field).url)
            obj.clean()
            obj.save()
            response_data = {'detail': 'File uploaded correctly'}
            return Response(response_data, status=status.HTTP_200_OK)
    
    return UploadFile


class Update(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/server/do-update`](
        http://confine-project.eu/rel/server/do-update)
    
    Contains the function URI used to update this sliver.
    
    POST data: `null`
    """
    url_name = 'update'
    rel = 'http://confine-project.eu/rel/server/do-update'
    
    def post(self, request, *args, **kwargs):
        if not request.DATA:
            sliver = get_object_or_404(Sliver, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, sliver)
            sliver.update()
            response_data = {'detail': 'Sliver instructed to update'}
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        raise exceptions.ParseError(detail='This endpoint only accepts null data')


class SliceList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Slice.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#slice_at_server)
    
    This resource lists the [slices](http://wiki.confine-project.eu/arch:rest-
    api?&#slice_at_server) present in the testbed and provides API URIs to
    navigate to them.
    """
    model = Slice
    add_serializer_class = SliceCreateSerializer
    serializer_class = SliceSerializer
    filter_fields = ('set_state', )


class SliceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Slice.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#slice_at_server)
    
    This resource describes a slice in the testbed, including its [slivers](
        http://wiki.confine-project.eu/arch:rest-api?&#sliver_at_server) with API
    URIs to navigate to them.
    """
    model = Slice
    serializer_class = SliceSerializer
    ctl = [
        Renew, Reset, make_upload_file(Slice, 'exp_data', 'exp-data'),
        make_upload_file(Slice, 'overlay', 'overlay'),
    ]


class SliverList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Sliver.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#sliver_at_server)
    
    This resource lists the [slivers](http://wiki.confine-project.eu/arch:rest-
    api?&#sliver_at_server) present in the testbed and provides API URIs to
    navigate to them.
    """
    model = Sliver
    serializer_class = SliverSerializer
    filter_fields = ('node', 'slice')


class SliverDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Sliver.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#sliver_at_server)
    
    This resource describes a sliver in the testbed, with API URIs to navigate
    to the [slice](http://wiki.confine-project.eu/arch:rest-api?&#slice_at_server)
    it is part of and the [node](http://wiki.confine-project.eu/arch:rest-api?
    &#node_at_server) it is intended to run on.
    """
    model = Sliver
    serializer_class = SliverDetailSerializer
    ctl = [
        Update, make_upload_file(Sliver, 'exp_data', 'exp-data'),
        make_upload_file(Sliver, 'overlay', 'overlay'),
    ]


class TemplateList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Template.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#template_at_server)
    
    This resource lists the sliver [templates](http://wiki.confine-project.eu/
    arch:rest-api?&#template_at_server) available in the testbed and provides
    API URIs to navigate to them.
    """
    model = Template
    serializer_class = TemplateSerializer


class TemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Template.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#template_at_server)
    
    This resource describes a template available in the testbed for [slices](
    http://wiki.confine-project.eu/arch:rest-api?&#slice_at_server) and
    [slivers](http://wiki.confine-project.eu/arch:rest-api?&#sliver_at_server)
    to use.
    """
    model = Template
    serializer_class = TemplateSerializer
    ctl = [
        make_upload_file(Template, 'image', 'image'),
    ]


api.register(SliceList, SliceDetail)
api.register(SliverList, SliverDetail)
api.register(TemplateList, TemplateDetail)
