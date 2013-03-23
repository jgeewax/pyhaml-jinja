import unittest2

from pyhaml_jinja.errors import TemplateIndentationError, TemplateSyntaxError
from pyhaml_jinja.parser import Parser
from pyhaml_jinja.nodes import Node, EmptyNode, HtmlNode, TextNode


class TestParserGetSourceLines(unittest2.TestCase):

  def test_empty(self):
    self.assertEqual([''], Parser.get_source_lines(''))
    self.assertEqual([''], Parser.get_source_lines(None))

  def test_basic(self):
    source = (
        '%div\n'
        '  text\n'
        '%p\n'
        '  %p\n'
        '    nested-text\n'
        )

    lines = Parser.get_source_lines(source)
    self.assertEqual(5, len(lines))
    self.assertEqual(['%div', '  text', '%p', '  %p', '    nested-text'], lines)

  def test_comment(self):
    source = (
        '%div\n'
        '; comment\n'
        '  text\n'
        )
    lines = Parser.get_source_lines(source)
    self.assertEqual(3, len(lines))
    self.assertEqual(['%div', '; comment', '  text'], lines)

  def test_line_continuation(self):
    source = (
        '%div(a="1", \\\n'
        '     b="2")\n'
        '  text\n'
        )
    lines = Parser.get_source_lines(source)
    self.assertEqual(3, len(lines))
    self.assertEqual(['%div(a="1", b="2")', '', '  text'], lines)


class TestParserGetIndentLevel(unittest2.TestCase):

  def test_empty(self):
    self.assertEqual(0, Parser.get_indent_level(''))
    self.assertEqual(0, Parser.get_indent_level('f'))
  
  def test_four(self):
    self.assertEqual(4, Parser.get_indent_level('    f'))

  def test_whitespace_only(self):
    # get_source_lines should strip these, but get_indent_level respects
    # whitespace-only lines.
    self.assertEqual(4, Parser.get_indent_level('    '))

  def test_mixed_tabs_and_spaces_raises_error(self):
    with self.assertRaises(ValueError):
      Parser.get_indent_level('  \t  foo')

  def test_mixed_tabs_and_spaces_raises_indentation_error_in_build_tree(self):
    source = (
        '  \ttext\n'
        )
    with self.assertRaises(TemplateIndentationError):
      Parser.build_tree(source)

  def test_invalid_indentation_raises_error(self):
    source = (
        '%div\n'
        '  f\n'
        ' f\n'
        '       f\n'
        '    f\n'
        )
    with self.assertRaises(TemplateIndentationError):
      Parser.build_tree(source)


class TestParserBuildTree(unittest2.TestCase):

  def test_empty(self):
    tree = Parser.build_tree('')
    self.assertTrue(tree.has_children())
    self.assertEqual(1, len(tree.get_children()))
    self.assertIsInstance(tree.get_children()[0], EmptyNode)

  def test_single_child(self):
    source = ('%div')
    tree = Parser.build_tree(source)
    self.assertTrue(tree.has_children())
    self.assertEqual(1, len(tree.get_children()))

  def test_single_line_continuation(self):
    source = (
        '%div(a="1", \\ \n'
        '     b="2")\n'
        )
    tree = Parser.build_tree(source)
    self.assertTrue(tree.has_children())
    self.assertEqual(1, len(tree.get_children()))

  def test_tree_basic(self):
    source = '%div.cls inline content'
    tree = Parser.build_tree(source)
    lines = tree.render_lines()
    self.assertEqual(['<div class="cls">', 'inline content', '</div>'], lines)

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
    source = '%div(a="1" b="2")' # Missing comma!
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



class TestParserParseLine(unittest2.TestCase):

  def test_single_html_tag(self):
    line = '%div'
    node = Parser.parse_line(line)
    self.assertFalse(node.has_children())
    self.assertIsInstance(node, HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)

  def test_shortcut_class(self):
    line = '.cls'
    node = Parser.parse_line(line)
    self.assertIsInstance(node, HtmlNode)
    self.assertFalse(node.has_children())
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'cls'}, node.attributes)

  def test_shortcut_id(self):
    line = '#myid'
    node = Parser.parse_line(line)
    self.assertIsInstance(node, HtmlNode)
    self.assertFalse(node.has_children())
    self.assertEqual('div', node.tag)
    self.assertEqual({'id': 'myid'}, node.attributes)

  def test_text(self):
    line = 'this is some text'
    node = Parser.parse_line(line)
    self.assertIsInstance(node, TextNode)
    self.assertEqual('this is some text', node.data)


class TestParserRenderHtml(unittest2.TestCase):

  def test_basic(self):
    source = (
        '%div\n'
        '  text\n'
        )
    parser = Parser(source)
    html = parser.render()
    self.assertEqual('<div>text</div>', html)

  def test_with_newlines(self):
    source = (
        '%div\n'
        '  %p text\n'
        '  text2\n'
        )
    parser = Parser(source, newline_string='\n')
    html = parser.render()
    self.assertEqual((
      '<div>\n'
      '<p>\n'
      'text\n'
      '</p>\n'
      'text2\n'
      '</div>'
      ), html)

  def test_with_newlines_and_indentation(self):
    source = (
        '%div\n'
        '  %p text\n'
        '  text2\n'
        )
    parser = Parser(source, newline_string='\n', indent_string='  ')
    html = parser.render()
    self.assertEqual((
      '<div>\n'
      '  <p>\n'
      '    text\n'
      '  </p>\n'
      '  text2\n'
      '</div>'
      ), html)


