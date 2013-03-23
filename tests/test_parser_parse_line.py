import unittest2

from pyhaml_jinja import nodes
from pyhaml_jinja.parser import Parser


class TestParserParseLine(unittest2.TestCase):

  def test_single_html_tag(self):
    line = '%div'
    node = Parser.parse_line(line)
    self.assertFalse(node.has_children())
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertEqual('div', node.tag)
    self.assertEqual({}, node.attributes)

  def test_shortcut_class(self):
    line = '.cls'
    node = Parser.parse_line(line)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertFalse(node.has_children())
    self.assertEqual('div', node.tag)
    self.assertEqual({'class': 'cls'}, node.attributes)

  def test_shortcut_id(self):
    line = '#myid'
    node = Parser.parse_line(line)
    self.assertIsInstance(node, nodes.HtmlNode)
    self.assertFalse(node.has_children())
    self.assertEqual('div', node.tag)
    self.assertEqual({'id': 'myid'}, node.attributes)

  def test_text(self):
    line = 'this is some text'
    node = Parser.parse_line(line)
    self.assertIsInstance(node, nodes.TextNode)
    self.assertEqual('this is some text', node.data)

