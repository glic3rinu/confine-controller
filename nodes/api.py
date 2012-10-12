from controller import api
from nodes.views import Nodes, Node

api.register((Nodes, Node), 'node')
