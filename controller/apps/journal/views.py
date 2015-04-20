from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from nodes.models import Node
from slices.models import Sliver


class NodeSliverListView(TemplateView):
    template_name = "public/node_sliver_list.html"
    
    def get_context_data(self, object_id, **kwargs):
        context = super(NodeSliverListView, self).get_context_data(**kwargs)
        context['node'] = get_object_or_404(Node, pk=object_id)
        # TODO(santiago) sliver start and end date
        # Implement some log? slice creation, first and last sliver added
        return context


class NodeSliverDetailView(TemplateView):
    template_name = 'public/node_sliver_detail.html'
    
    def get_context_data(self, object_id, **kwargs):
        context = super(NodeSliverDetailView, self).get_context_data(**kwargs)
        context['sliver'] = get_object_or_404(Sliver, pk=object_id)
        return context
