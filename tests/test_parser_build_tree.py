import unittest2

from pyhaml_jinja import nodes
from pyhaml_jinja.errors import TemplateIndentationError, TemplateSyntaxError
from pyhaml_jinja.parser import Parser


class TestParserBuildTree(unittest2.TestCase):

  def test_empty(self):
    tree = Parser.build_tree('')
    self.assertFalse(tree.has_children())

  def test_single_child(self):
    source = ('%div')
    tree = Parser.build_tree(source)
    self.assertTrue(tree.has_children())
    self.assertEqual(1, len(tree.get_children()))

    node = tree.get_children()[0]
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)

  def test_single_line_continuation(self):
    source = (
        '%div(a="1", \\ \n'
        '     b="2")\n'
        )
    tree = Parser.build_tree(source)
    self.assertTrue(tree.has_children())
    self.assertEqual(1, len(tree.get_children()))

    node = tree.get_children()[0]
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'a': '1', 'b': '2'}, node.attributes)

  def test_inline_content(self):
    source = '%div.cls inline content'
    tree = Parser.build_tree(source)
    self.assertEqual(1, len(tree.get_children()))

    node = tree.get_children()[0]
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'cls'}, node.attributes)

    self.assertEqual(1, len(node.get_children()))
    text_node = node.get_children()[0]
    self.assertIsInstance(text_node, nodes.TextNode)
    self.assertEqual('inline content', text_node.data)

  def test_tree_nested(self):
    source = (
        '%div(a="1", \\ \n'
        '     b="2")\n'
        '  %h1 heading 1\n'
        '  %p: %span: %b bold nested\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['<div a="1" b="2">', '<h1>', 'heading 1', '</h1>', '<p>',
                      '<span>', '<b>', 'bold nested', '</b>', '</span>',
                      '</p>', '</div>'], lines)

  def test_line_continuation_in_if_statement(self):
    source = (
        '-if True\n'
        '  %link(a="1", \\\n'
        '        b="2")\n'
        '  %script(c="3")\n'
        '-else\n'
        '  %link(d="4")\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['{% if True %}', '<link a="1" b="2" />',
                      '<script c="3">','</script>', '{% else %}',
                      '<link d="4" />', '{% endif %}'], lines)

  def test_tree_text(self):
    source = (
        '%div\n'
        '  text\n'
        '  text2\n'
        'top level text\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['<div>', 'text', 'text2', '</div>', 'top level text'],
                     lines)

  def test_tree_invalid_attributes(self):
    source = '%div(a="1" b="2")'  # Missing comma!
    with self.assertRaises(TemplateSyntaxError):
      tree = Parser.build_tree(source)

  def test_tree_text_with_unusual_indentation(self):
    source = (
        'text on base line\n'
        '  indented for no good reason\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['text on base line', 'indented for no good reason'],
                     lines)

  def test_mixed_tabs_and_spaces(self):
    source = (
        '  \ttext\n'
        )
    with self.assertRaises(TemplateIndentationError):
      Parser.build_tree(source)

  def test_invalid_indentation(self):
    source = (
        '%div\n'
        '  f\n'
        ' f\n'
        '       f\n'
        '    f\n'
        )
    with self.assertRaises(TemplateIndentationError):
      Parser.build_tree(source)

  def test_tree_text_with_html_child(self):
    source = (
        'text on base line\n'
        '  %div\n'
        )

    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['text on base line', '<div>', '</div>'], lines)

  def test_tree_children_of_childless_node(self):
    source = (
        '%hr\n'
        '  text\n'
        )
    with self.assertRaises(TemplateSyntaxError):
      Parser.build_tree(source)

  def test_tree_raw_jinja_tag_with_a_div(self):
    source = (
        '{% if True %}\n'
        '  %div true text\n'
        '{% endif %}\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['{% if True %}', '<div>', 'true text', '</div>',
                      '{% endif %}'], lines)

  def test_tree_jinja_tag_if_else(self):
    source = (
        '-if True\n'
        '  %div true\n'
        '-else\n'
        '  %div false\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['{% if True %}', '<div>', 'true', '</div>', '{% else %}',
                      '<div>', 'false', '</div>', '{% endif %}'], lines)

  def test_tree_jinja_tag_if_elif_elif_else(self):
    source = (
        '-if 1\n'
        '  1\n'
        '-elif 2\n'
        '  2\n'
        '-elif 3\n'
        '  3\n'
        '-else\n'
        '  4\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['{% if 1 %}', '1', '{% elif 2 %}', '2', '{% elif 3 %}',
                      '3', '{% else %}', '4', '{% endif %}'], lines)

  def test_tree_jinja_tag_for(self):
    source = (
        '-for item in list\n'
        '  item\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['{% for item in list %}', 'item', '{% endfor %}'], lines)

  def test_tree_jinja_tag_for_else(self):
    source = (
        '-for item in list\n'
        '  item\n'
        '-else\n'
        '  empty\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['{% for item in list %}', 'item', '{% else %}', 'empty',
                      '{% endfor %}'], lines)

  def test_tree_jinja_tags_empty(self):
    source = (
        '-for item in list\n'
        '-if True\n'
        'top\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['{% for item in list %}', '{% endfor %}',
                      '{% if True %}', '{% endif %}', 'top'], lines)

  def test_tree_jinja_tags_self_closing(self):
    source = (
        '-extends "base.haml"\n'
        'text\n'
        )
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['{% extends "base.haml" %}', 'text'], lines)

  def test_tree_jinja_tag_followed_by_html_tag(self):
    source = (
        '%html\n'
        '  -for item in items\n'
        '    #{item}\n'
        '  -else\n'
        '    Empty\n'
        '  %div(a="1", \\ \n'
        '       b="2")\n'
        )
    tree = Parser.build_tree(source)
    self.assertIsInstance(tree, nodes.Node)
    lines = tree.render_lines()
    self.assertEqual(['<html>', '{% for item in items %}', '{{ item }}',
                      '{% else %}', 'Empty', '{% endfor %}',
                      '<div a="1" b="2">', '</div>', '</html>'], lines)

