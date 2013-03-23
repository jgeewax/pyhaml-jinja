import unittest2

from pyhaml_jinja import nodes


class TestNode(unittest2.TestCase):

  def test_node_starts_without_children(self):
    node = nodes.Node()
    self.assertEqual(0, len(node.children))

  def test_node_has_children(self):
    node = nodes.Node()
    self.assertFalse(node.has_children())
    
    node.add_child(nodes.Node())
    self.assertTrue(node.has_children())

  def test_node_cant_add_non_node(self):
    node = nodes.Node()
    with self.assertRaises(ValueError):
      node.add_child(5)

  def test_node_children_allowed_by_default(self):
    node = nodes.Node()
    self.assertTrue(node.children_allowed())

  def test_node_render_start_defauts_to_None(self):
    node = nodes.Node()
    self.assertEqual(None, node.render_start())

  def test_node_render_end_defaults_to_None(self):
    node = nodes.Node()
    self.assertEqual(None, node.render_end())

  def test_parent_set_when_child_added(self):
    parent = nodes.Node()
    self.assertEqual(None, parent.parent)
    child = nodes.Node()
    self.assertEqual(None, child.parent)
    parent.add_child(child)
    self.assertEqual(None, parent.parent)
    self.assertEqual(parent, child.parent)

  def test_adding_child_twice_throws_error(self):
    parent1 = nodes.Node()
    parent2 = nodes.Node()
    child = nodes.Node()
    self.assertEqual(None, child.parent)
    parent1.add_child(child)
    self.assertEqual(parent1, child.parent)
    self.assertEqual(1, len(parent1.get_children()))

    with self.assertRaises(RuntimeError):
      parent2.add_child(child)

    self.assertFalse(parent2.has_children())
    self.assertEqual(parent1, child.parent)

