from nodes.models import Node
from nodes.serializers import NodeSerializer
from rest_framework import generics
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class NodeRoot(generics.ListCreateAPIView):
    model = Node
    serializer_class = NodeSerializer

class APIRootView(APIView):
    def get(self, request):
        data = {
            'url': reverse('node_instance', request, args=[])
        }
        return Response(data)



class NodeInstance(generics.RetrieveUpdateDestroyAPIView):
    model = Node
    serializer_class = NodeSerializer

