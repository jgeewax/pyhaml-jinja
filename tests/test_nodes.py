import unittest2

from pyhaml_jinja.nodes import (
    Node, ChildlessNode, HtmlNode, JinjaNode, SelfClosingHtmlNode,
    SelfClosingJinjaNode, TextNode)


class TestNode(unittest2.TestCase):

  def test_node_starts_without_children(self):
    node = Node()
    self.assertEqual(0, len(node.children))

  def test_node_has_children(self):
    node = Node()
    self.assertFalse(node.has_children())
    
    node.add_child(Node())
    self.assertTrue(node.has_children())

  def test_node_cant_add_non_node(self):
    node = Node()
    with self.assertRaises(ValueError):
      node.add_child(5)

  def test_node_children_allowed_by_default(self):
    node = Node()
    self.assertTrue(node.children_allowed())

  def test_node_render_start_defauts_to_None(self):
    node = Node()
    self.assertEqual(None, node.render_start())

  def test_node_render_end_defaults_to_None(self):
    node = Node()
    self.assertEqual(None, node.render_end())

  def test_parent_set_when_child_added(self):
    parent = Node()
    self.assertEqual(None, parent.parent)
    child = Node()
    self.assertEqual(None, child.parent)
    parent.add_child(child)
    self.assertEqual(None, parent.parent)
    self.assertEqual(parent, child.parent)

  def test_adding_child_twice_throws_error(self):
    parent1 = Node()
    parent2 = Node()
    child = Node()
    self.assertEqual(None, child.parent)
    parent1.add_child(child)
    self.assertEqual(parent1, child.parent)
    self.assertEqual(1, len(parent1.get_children()))

    with self.assertRaises(RuntimeError):
      parent2.add_child(child)

    self.assertFalse(parent2.has_children())
    self.assertEqual(parent1, child.parent)


class TestNodeGetSiblings(unittest2.TestCase):

  def test_get_siblings_no_parent(self):
    node = Node()
    self.assertEqual(None, node.get_previous_sibling())
    self.assertEqual(None, node.get_next_sibling())

  def test_get_siblings_only_child(self):
    parent = Node()
    child = Node()
    parent.add_child(child)
    self.assertEqual(None, child.get_previous_sibling())
    self.assertEqual(None, child.get_next_sibling())

  def test_get_siblings_first_child(self):
    parent = Node()
    child1 = Node()
    child2 = Node()
    parent.add_child(child1)
    parent.add_child(child2)
    self.assertEqual(None, child1.get_previous_sibling())
    self.assertEqual(child2, child1.get_next_sibling())
    self.assertEqual(child1, child2.get_previous_sibling())
    self.assertEqual(None, child2.get_next_sibling())

  def test_get_siblings_middle_child(self):
    parent = Node()
    child1 = Node()
    child2 = Node()
    child3 = Node()
    parent.add_child(child1)
    parent.add_child(child2)
    parent.add_child(child3)
    self.assertEqual(child1, child2.get_previous_sibling())
    self.assertEqual(child3, child2.get_next_sibling())


class TestNodeRenderLines(unittest2.TestCase):

  def test_simple(self):
    node = HtmlNode('div')
    lines = node.render_lines()
    self.assertEqual(['<div>', '</div>'], lines)

  def test_simple_content(self):
    node = HtmlNode('div')
    node.add_child(TextNode('content'))
    lines = node.render_lines()
    self.assertEqual(['<div>', 'content', '</div>'], lines)

  def test_nested(self):
    parent = HtmlNode('div')
    child = HtmlNode('p')
    text = TextNode('content')
    parent.add_child(child)
    child.add_child(text)

    lines = parent.render_lines()
    self.assertEqual(['<div>', '<p>', 'content', '</p>', '</div>'], lines)

  def test_multiple_trees(self):
    parent = HtmlNode('div')
    child1 = HtmlNode('p')
    child2 = HtmlNode('span')
    child1.add_child(TextNode('ptext'))
    child2.add_child(TextNode('spantext'))
    parent.add_child(child1)
    parent.add_child(child2)

    lines = parent.render_lines()
    self.assertEqual(['<div>', '<p>', 'ptext', '</p>', '<span>', 'spantext',
                      '</span>', '</div>'], lines)


class TestChildlessNode(unittest2.TestCase):

  def test_children_allowed_false(self):
    node = ChildlessNode()
    self.assertFalse(node.children_allowed())

  def test_adding_child_fails(self):
    node = ChildlessNode()
    with self.assertRaises(RuntimeError):
      node.add_child(Node())


class TestTextNode(unittest2.TestCase):

  def test_properly_stores_data(self):
    node = TextNode('data')
    self.assertEqual('data', node.data)

  def test_requires_data_at_instantiation(self):
    with self.assertRaises(Exception):
      node = TextNode()

  def test_render_start_shows_just_data(self):
    node = TextNode('data')
    self.assertEqual('data', node.render_start())

  def test_render_end_is_None(self):
    node = TextNode('data')
    self.assertEqual(None, node.render_end())


class TestHtmlNode(unittest2.TestCase):

  def test_stores_tag_and_attribute_dictionary(self):
    node = HtmlNode('div', {'class': 'foo'})
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'foo'}, node.attributes)

  def test_attributes_are_optional(self):
    node = HtmlNode('div')
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)

  def test_duplicate_attributes_only_allowed_for_class(self):
    node = HtmlNode('div')
    self.assertEqual({}, node.attributes)

    node.add_attribute('foo', 'bar')
    self.assertEqual({'foo': 'bar'}, node.attributes)

    with self.assertRaises(KeyError):
      node.add_attribute('foo', 'other')

    self.assertEqual({'foo': 'bar'}, node.attributes)

    node.add_attribute('class', 'cls1')
    self.assertEqual({'foo': 'bar', 'class': 'cls1'}, node.attributes)
    node.add_attribute('class', 'cls2')
    self.assertEqual({'foo': 'bar', 'class': 'cls1 cls2'}, node.attributes)

  def test_private_render_attributes(self):
    attributes = {'a': '1', 'b': '2'}
    self.assertEqual('a="1" b="2"', HtmlNode._render_attributes(attributes))

    self.assertEqual('', HtmlNode._render_attributes({}))
    self.assertEqual('', HtmlNode._render_attributes(None))

  def test_render_attributes(self):
    node = HtmlNode('div', {'a': '1', 'b': '2'})
    self.assertEqual('a="1" b="2"', node.render_attributes())

  def test_render_start(self):
    node = HtmlNode('div', {'a': '1', 'b': '2'})
    self.assertEqual('<div a="1" b="2">', node.render_start())

    node = HtmlNode('div')
    self.assertEqual('<div>', node.render_start())

  def test_render_end(self):
    node = HtmlNode('div', {'a': '1', 'b': '2'})
    self.assertEqual('</div>', node.render_end())

    node = HtmlNode('div')
    self.assertEqual('</div>', node.render_end())

  def test_from_haml_basic(self):
    haml = '%div'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)

  def test_from_haml_invalid_line(self):
    haml = '%%%%...####'
    with self.assertRaises(ValueError):
      node = HtmlNode.from_haml(haml)

  def test_from_haml_with_class_shortcut(self):
    haml = '.cls'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'cls'}, node.attributes)

  def test_from_haml_with_id_shortcut(self):
    haml = '#myid'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'id': 'myid'}, node.attributes)

  def test_from_haml_with_multiple_classes(self):
    haml = '.cls1.cls2.cls3'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'cls1 cls2 cls3'}, node.attributes)

  def test_from_haml_mix_shortcuts_id_and_classes(self):
    haml = '#myid.cls1.cls2'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'id': 'myid', 'class': 'cls1 cls2'}, node.attributes)

  def test_from_haml_with_class_shortcut_and_attrs(self):
    haml = '.cls(a="1", b="2")'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'cls', 'a': '1', 'b': '2'}, node.attributes)
  
  def test_from_haml_with_attrs_including_commas(self):
    haml = '%div(a="1", b="with, commas")'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'a': '1', 'b': 'with, commas'}, node.attributes)

  def test_from_haml_with_inline_content(self):
    haml = '%div inline content'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)
    self.assertTrue(node.has_children())
    
    child = node.get_children()[0]
    self.assertIsInstance(child, TextNode)
    self.assertEqual('inline content', child.data)

  def test_from_haml_with_inline_content_on_self_closing_tag(self):
    haml = '%hr with content'
    with self.assertRaises(ValueError):
      node = HtmlNode.from_haml(haml)

  def test_from_haml_with_nested_tag(self):
    haml = '%div: %div'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)
    self.assertTrue(node.has_children())
    self.assertEqual(1, len(node.get_children()))

    child = node.get_children()[0]
    self.assertIsInstance(child, HtmlNode)
    self.assertEqual('div', child.tag)
    self.assertEqual({}, child.attributes)
    self.assertFalse(child.has_children())

  def test_from_haml_not_nested_but_with_colon(self):
    haml = '%div my inline text: is here'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)
    self.assertTrue(node.has_children())
    self.assertEqual(1, len(node.get_children()))

    child = node.get_children()[0]
    self.assertIsInstance(child, TextNode)
    self.assertEqual('my inline text: is here', child.data)

  def test_from_haml_nested_with_inline_content(self):
    haml = '%div: %div inline content'
    node = HtmlNode.from_haml(haml)
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)
    self.assertTrue(node.has_children())
    self.assertEqual(1, len(node.get_children()))

    child = node.get_children()[0]
    self.assertIsInstance(child, HtmlNode)
    self.assertEqual('div', child.tag)
    self.assertEqual({}, child.attributes)
    self.assertTrue(child.has_children())
    self.assertEqual(1, len(child.get_children()))

    text = child.get_children()[0]
    self.assertIsInstance(text, TextNode)
    self.assertEqual('inline content', text.data)

  def test_from_haml_self_closing(self):
    for tag in HtmlNode.SELF_CLOSING_TAGS:
      haml = '%' + tag
      node = HtmlNode.from_haml(haml)
      self.assertIsInstance(node, SelfClosingHtmlNode)
      self.assertEqual(tag, node.tag)
      self.assertEqual({}, node.attributes)
      self.assertFalse(node.has_children())


class TestSelfClosingHtmlNode(unittest2.TestCase):

  def test_render_start_self_closes(self):
    node = SelfClosingHtmlNode('div', {'a': '1', 'b': '2'})
    self.assertEqual('<div a="1" b="2" />', node.render_start())

    node = SelfClosingHtmlNode('div')
    self.assertEqual('<div />', node.render_start())

  def test_render_end_is_None(self):
    node = SelfClosingHtmlNode('div', {'a': '1', 'b': '2'})
    self.assertEqual(None, node.render_end())

    node = SelfClosingHtmlNode('div')
    self.assertEqual(None, node.render_end())


class TestJinjaNode(unittest2.TestCase):

  def test_render_start_just_tag(self):
    node = JinjaNode('block')
    self.assertEqual('{% block %}', node.render_start())

  def test_render_start_with_data(self):
    node = JinjaNode('if', 'data == "data"')
    self.assertEqual('{% if data == "data" %}', node.render_start())

  def test_render_end_just_tag(self):
    node = JinjaNode('block')
    self.assertEqual('{% endblock %}', node.render_end())

  def test_render_end_with_data(self):
    node = JinjaNode('if', 'data == "data"')
    self.assertEqual('{% endif %}', node.render_end())

  def test_from_haml_basic(self):
    haml = '-if True'
    node = JinjaNode.from_haml(haml)
    self.assertEqual('if', node.tag)
    self.assertEqual('True', node.data)

  def test_from_haml_invalid_string(self):
    haml = '-.....'
    with self.assertRaises(ValueError):
      node = JinjaNode.from_haml(haml)

  def test_from_haml_self_closing_tag(self):
    haml = '-extends "base.haml"'
    node = JinjaNode.from_haml(haml)
    self.assertEqual('extends', node.tag)
    self.assertEqual('"base.haml"', node.data)
    self.assertIsInstance(node, SelfClosingJinjaNode)

