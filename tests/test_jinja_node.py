import unittest2

from pyhaml_jinja import nodes


class TestJinjaNode(unittest2.TestCase):

  def test_repr(self):
    node = nodes.JinjaNode('extends')
    self.assertEqual('<JinjaNode: extends  0 children>', repr(node))

  def test_render_start_just_tag(self):
    node = nodes.JinjaNode('block')
    self.assertEqual('{% block %}', node.render_start())

  def test_render_start_with_data(self):
    node = nodes.JinjaNode('if', 'data == "data"')
    self.assertEqual('{% if data == "data" %}', node.render_start())

  def test_render_end_just_tag(self):
    node = nodes.JinjaNode('block')
    self.assertEqual('{% endblock %}', node.render_end())

  def test_render_end_with_data(self):
    node = nodes.JinjaNode('if', 'data == "data"')
    self.assertEqual('{% endif %}', node.render_end())

  def test_from_haml_basic(self):
    haml = '-if True'
    node = nodes.JinjaNode.from_haml(haml)
    self.assertEqual('if', node.tag)
    self.assertEqual('True', node.data)

  def test_from_haml_invalid_string(self):
    haml = '-.....'
    with self.assertRaises(ValueError):
      node = nodes.JinjaNode.from_haml(haml)

  def test_from_haml_self_closing_tag(self):
    haml = '-extends "base.haml"'
    node = nodes.JinjaNode.from_haml(haml)
    self.assertEqual('extends', node.tag)
    self.assertEqual('"base.haml"', node.data)
    self.assertIsInstance(node, nodes.SelfClosingJinjaNode)

  def test_from_haml_inline_content(self):
    haml = '-if a == "2": text'
    node = nodes.JinjaNode.from_haml(haml)
    self.assertIsInstance(node, nodes.JinjaNode)
    self.assertEqual('if', node.tag)
    self.assertEqual('a == "2"', node.data)
    self.assertTrue(node.has_children())
    self.assertEqual(1, len(node.get_children()))

    child = node.get_children()[0]
    self.assertIsInstance(child, nodes.TextNode)
    self.assertEqual('text', child.data)
    self.assertFalse(child.has_children())

  def test_from_haml_nested_jinja_tags(self):
    haml = '-if a == "2": -if b == "3": content'
    node = nodes.JinjaNode.from_haml(haml)
    self.assertIsInstance(node, nodes.JinjaNode)
    self.assertEqual('if', node.tag)
    self.assertEqual('a == "2"', node.data)
    self.assertTrue(node.has_children())
    self.assertEqual(1, len(node.get_children()))

    child1 = node.get_children()[0]
    self.assertIsInstance(child1, nodes.JinjaNode)
    self.assertEqual('if', child1.tag)
    self.assertEqual('b == "3"', child1.data)
    self.assertTrue(child1.has_children())
    self.assertEqual(1, len(child1.get_children()))

    child2 = child1.get_children()[0]
    self.assertIsInstance(child2, nodes.TextNode)
    self.assertEqual('content', child2.data)
    self.assertFalse(child2.has_children())

  def test_from_haml_nested_tags_with_dictionary(self):
    haml = '-if {\'a\': \'b\'}: -if list[:]: -if ":": content'
    node = nodes.JinjaNode.from_haml(haml)
    self.assertIsInstance(node, nodes.JinjaNode)
    self.assertEqual('if', node.tag)
    self.assertEqual('{\'a\': \'b\'}', node.data)
    self.assertTrue(node.has_children())
    self.assertEqual(1, len(node.get_children()))

    child1 = node.get_children()[0]
    self.assertIsInstance(child1, nodes.JinjaNode)
    self.assertEqual('if', child1.tag)
    self.assertEqual('list[:]', child1.data)
    self.assertTrue(child1.has_children())
    self.assertEqual(1, len(child1.get_children()))

    child2 = child1.get_children()[0]
    self.assertIsInstance(child2, nodes.JinjaNode)
    self.assertEqual('if', child2.tag)
    self.assertEqual('":"', child2.data)
    self.assertTrue(child2.has_children())
    self.assertEqual(1, len(child2.get_children()))

    child3 = child2.get_children()[0]
    self.assertIsInstance(child3, nodes.TextNode)
    self.assertEqual('content', child3.data)
    self.assertFalse(child3.has_children())

