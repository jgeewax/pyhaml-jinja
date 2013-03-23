import unittest2

from pyhaml_jinja import nodes


class TestHtmlNode(unittest2.TestCase):

  def test_stores_tag_and_attribute_dictionary(self):
    node = nodes.HtmlNode('div', {'class': 'foo'})
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'foo'}, node.attributes)

  def test_attributes_are_optional(self):
    node = nodes.HtmlNode('div')
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)

  def test_duplicate_attributes_only_allowed_for_class(self):
    node = nodes.HtmlNode('div')
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
    self.assertEqual('a="1" b="2"', nodes.HtmlNode._render_attributes(attributes))

    self.assertEqual('', nodes.HtmlNode._render_attributes({}))
    self.assertEqual('', nodes.HtmlNode._render_attributes(None))

  def test_render_attributes(self):
    node = nodes.HtmlNode('div', {'a': '1', 'b': '2'})
    self.assertEqual('a="1" b="2"', node.render_attributes())

  def test_render_start(self):
    node = nodes.HtmlNode('div', {'a': '1', 'b': '2'})
    self.assertEqual('<div a="1" b="2">', node.render_start())

    node = nodes.HtmlNode('div')
    self.assertEqual('<div>', node.render_start())

  def test_render_end(self):
    node = nodes.HtmlNode('div', {'a': '1', 'b': '2'})
    self.assertEqual('</div>', node.render_end())

    node = nodes.HtmlNode('div')
    self.assertEqual('</div>', node.render_end())

  def test_from_haml_basic(self):
    haml = '%div'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)

  def test_from_haml_invalid_line(self):
    haml = '%%%%...####'
    with self.assertRaises(ValueError):
      node = nodes.HtmlNode.from_haml(haml)

  def test_from_haml_with_class_shortcut(self):
    haml = '.cls'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'cls'}, node.attributes)

  def test_from_haml_with_id_shortcut(self):
    haml = '#myid'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'id': 'myid'}, node.attributes)

  def test_from_haml_with_multiple_classes(self):
    haml = '.cls1.cls2.cls3'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'cls1 cls2 cls3'}, node.attributes)

  def test_from_haml_mix_shortcuts_id_and_classes(self):
    haml = '#myid.cls1.cls2'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'id': 'myid', 'class': 'cls1 cls2'}, node.attributes)

  def test_from_haml_with_class_shortcut_and_attrs(self):
    haml = '.cls(a="1", b="2")'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'cls', 'a': '1', 'b': '2'}, node.attributes)
  
  def test_from_haml_with_attrs_including_commas(self):
    haml = '%div(a="1", b="with, commas")'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'a': '1', 'b': 'with, commas'}, node.attributes)

  def test_from_haml_with_inline_content(self):
    haml = '%div inline content'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)
    self.assertTrue(node.has_children())
    
    child = node.get_children()[0]
    self.assertIsInstance(child, nodes.TextNode)
    self.assertEqual('inline content', child.data)

  def test_from_haml_with_inline_content_on_self_closing_tag(self):
    haml = '%hr with content'
    with self.assertRaises(ValueError):
      node = nodes.HtmlNode.from_haml(haml)

  def test_from_haml_with_nested_tag(self):
    haml = '%div: %div'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)
    self.assertTrue(node.has_children())
    self.assertEqual(1, len(node.get_children()))

    child = node.get_children()[0]
    self.assertIsInstance(child, nodes.HtmlNode)
    self.assertEqual('div', child.tag)
    self.assertEqual({}, child.attributes)
    self.assertFalse(child.has_children())

  def test_from_haml_not_nested_but_with_colon(self):
    haml = '%div my inline text: is here'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)
    self.assertTrue(node.has_children())
    self.assertEqual(1, len(node.get_children()))

    child = node.get_children()[0]
    self.assertIsInstance(child, nodes.TextNode)
    self.assertEqual('my inline text: is here', child.data)

  def test_from_haml_nested_with_inline_content(self):
    haml = '%div: %div inline content'
    node = nodes.HtmlNode.from_haml(haml)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)
    self.assertTrue(node.has_children())
    self.assertEqual(1, len(node.get_children()))

    child = node.get_children()[0]
    self.assertIsInstance(child, nodes.HtmlNode)
    self.assertEqual('div', child.tag)
    self.assertEqual({}, child.attributes)
    self.assertTrue(child.has_children())
    self.assertEqual(1, len(child.get_children()))

    text = child.get_children()[0]
    self.assertIsInstance(text, nodes.TextNode)
    self.assertEqual('inline content', text.data)

  def test_from_haml_self_closing(self):
    for tag in nodes.HtmlNode.SELF_CLOSING_TAGS:
      haml = '%' + tag
      node = nodes.HtmlNode.from_haml(haml)
      self.assertIsInstance(node, nodes.SelfClosingHtmlNode)
      self.assertEqual(tag, node.tag)
      self.assertEqual({}, node.attributes)
      self.assertFalse(node.has_children())

