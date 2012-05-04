from django.db import models

class SliceManager(models.Manager):

    def from_node(self, node_id):
        query = self.filter(sliver__node__id = node_id)
        return query
