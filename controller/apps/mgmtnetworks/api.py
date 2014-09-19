from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils import insert_ctl
from nodes.api import NodeDetail
from nodes.models import Node

from .validators import validate_csr

class RequestCert(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/controller/do-request-mgmt-cert`](
        http://confine-project.eu/rel/controller/do-request-mgmt-cert)
    
    Contains the controller API function URI used to upload a certificate
    signing request (CSR) to be signed by the testbed CA. The distinguished
    name of the request must match this host's management address.
    
    POST data: `ASCII-armored PEM representation of the CSR as a string.`
    
    Response data: a JSON document with a `/cert` member containing the
    `ASCII-armored PEM representation of the signed certificate`.
    """
    url_name = 'request-cert'
    rel = 'http://confine-project.eu/rel/controller/do-request-mgmt-cert'
    
    def post(self, request, *args, **kwargs):
        csr = request.DATA
        node = get_object_or_404(Node, pk=kwargs.get('pk'))
        self.check_object_permissions(self.request, node)
        try:
            validate_csr(csr, node.mgmt_net.addr)
        except Exception as e:
            raise exceptions.ParseError(detail='Malformed CSR: %s' % e.message)
        signed_cert = node.mgmt_net.sign_cert_request(csr.strip())
        response_data = {'cert': signed_cert}
        return Response(response_data, status=status.HTTP_202_ACCEPTED)


insert_ctl(NodeDetail, RequestCert)
