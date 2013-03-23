import unittest2

from pyhaml_jinja import nodes


class TestNodeGetSiblings(unittest2.TestCase):

  def test_get_siblings_no_parent(self):
    node = nodes.Node()
    self.assertEqual(None, node.get_previous_sibling())
    self.assertEqual(None, node.get_next_sibling())

  def test_get_siblings_only_child(self):
    parent = nodes.Node()
    child = nodes.Node()
    parent.add_child(child)
    self.assertEqual(None, child.get_previous_sibling())
    self.assertEqual(None, child.get_next_sibling())

  def test_get_siblings_first_child(self):
    parent = nodes.Node()
    child1 = nodes.Node()
    child2 = nodes.Node()
    parent.add_child(child1)
    parent.add_child(child2)
    self.assertEqual(None, child1.get_previous_sibling())
    self.assertEqual(child2, child1.get_next_sibling())
    self.assertEqual(child1, child2.get_previous_sibling())
    self.assertEqual(None, child2.get_next_sibling())

  def test_get_siblings_middle_child(self):
    parent = nodes.Node()
    child1 = nodes.Node()
    child2 = nodes.Node()
    child3 = nodes.Node()
    parent.add_child(child1)
    parent.add_child(child2)
    parent.add_child(child3)
    self.assertEqual(child1, child2.get_previous_sibling())
    self.assertEqual(child3, child2.get_next_sibling())

