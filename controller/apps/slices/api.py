from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import Slice, Sliver, Template
from .serializers import SliceSerializer, SliverSerializer, TemplateSerializer


class Renew(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/server/do-renew`](
        http://confine-project.eu/rel/server/do-renew)
    
    Contains the function URI used to renew this slice.
    
    POST data: `null`
    """
    url_name = 'renew'
    
    def post(self, request, *args, **kwargs):
        if request.DATA is None:
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
    
    def post(self, request, *args, **kwargs):
        if request.DATA is None:
            slice = get_object_or_404(Slice, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, slice)
            slice.reset()
            response_data = {'detail': 'Slice instructed to reset'}
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        raise exceptions.ParseError(detail='This endpoint only accepts null data')


def make_upload_exp_data(model):
    class ExpDataSerializer(serializers.Serializer):
        """ Just for the browsable API """
        exp_data = serializers.FileField()
    
    # TODO ApiPermissionsMixin
    class UploadExpData(generics.CreateAPIView):
        """
        **Relation type:** [`http://confine-project.eu/rel/server/do-upload-exp-data`](
            http://confine-project.eu/rel/server/do-upload-exp-data)
        
        Contains the function URI used to upload this resource's experiment data file
        to some remote storage. The URI of the stored file will be placed in the
        `exp_data_uri` member and its hash in `exp_data_sha256`.
        
        POST data: `the contents of the file`
        
        Example: `curl -X POST -F "exp_data=@experiment_data.tgz" ...`
        """
        url_name = 'upload-exp-data'
        serializer_class = ExpDataSerializer
        
        def post(self, request, *args, **kwargs):
            if request.FILES and 'exp_data' in request.FILES:
                obj = get_object_or_404(model, pk=kwargs.get('pk'))
                self.check_object_permissions(self.request, obj)
                uploaded_file = request.FILES.get('exp_data')
                obj.exp_data.save(uploaded_file.name, uploaded_file)
                obj.clean()
                obj.save()
                response_data = {'detail': 'File uploaded correctly'}
                return Response(response_data, status=status.HTTP_200_OK)
            raise exceptions.ParseError(detail='This endpoint only accepts null data')
    return UploadExpData


class Update(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/server/do-update`](
        http://confine-project.eu/rel/server/do-update)
    
    Contains the function URI used to update this sliver.
    
    POST data: `null`
    """
    url_name = 'update'
    
    def post(self, request, *args, **kwargs):
        if request.DATA is None:
            sliver = get_object_or_404(Sliver, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, sliver)
            slice.update()
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
    ctl = [Renew, Reset, make_upload_exp_data(Slice)]


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
    filter_fields = ['slice__name', 'slice__set_state', 'node', 'node__id']
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
    serializer_class = SliverSerializer
    ctl = [Update, make_upload_exp_data(Sliver)]


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


api.register(SliceList, SliceDetail)
api.register(SliverList, SliverDetail)
api.register(TemplateList, TemplateDetail)
