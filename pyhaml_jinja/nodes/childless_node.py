from pyhaml_jinja.nodes.node import Node


__all__ = ['ChildlessNode']


class ChildlessNode(Node):

  def children_allowed(self):
    return False

