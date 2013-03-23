import unittest2

from pyhaml_jinja import nodes


class TestChildlessNode(unittest2.TestCase):

  def test_children_allowed_false(self):
    node = nodes.ChildlessNode()
    self.assertFalse(node.children_allowed())

  def test_adding_child_fails(self):
    node = nodes.ChildlessNode()
    with self.assertRaises(RuntimeError):
      node.add_child(nodes.Node())

