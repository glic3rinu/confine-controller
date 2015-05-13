from controller.admin.utils import insert_change_view_action
from nodes.models import Node

from .actions import show_node_slivers_journal


insert_change_view_action(Node, show_node_slivers_journal)
