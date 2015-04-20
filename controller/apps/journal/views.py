from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from nodes.models import Node

from .models import SliverLog


class NodeSliverListView(TemplateView):
    template_name = "public/node_sliver_list.html"
    
    def get_context_data(self, object_id, **kwargs):
        context = super(NodeSliverListView, self).get_context_data(**kwargs)
        node = get_object_or_404(Node, pk=object_id)
        slivers = SliverLog.objects.filter(node=node).order_by('created_on')
        context.update({
            'node': node,
            'slivers': slivers,
        })
        return context


class NodeSliverDetailView(TemplateView):
    template_name = 'public/node_sliver_detail.html'
    
    def get_context_data(self, object_id, **kwargs):
        context = super(NodeSliverDetailView, self).get_context_data(**kwargs)
        context['sliver'] = get_object_or_404(SliverLog, pk=object_id)
        return context
