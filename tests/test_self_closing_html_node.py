import unittest2

from pyhaml_jinja import nodes


class TestSelfClosingHtmlNode(unittest2.TestCase):

  def test_render_start_self_closes(self):
    node = nodes.SelfClosingHtmlNode('div', {'a': '1', 'b': '2'})
    self.assertEqual('<div a="1" b="2" />', node.render_start())

    node = nodes.SelfClosingHtmlNode('div')
    self.assertEqual('<div />', node.render_start())

  def test_render_end_is_None(self):
    node = nodes.SelfClosingHtmlNode('div', {'a': '1', 'b': '2'})
    self.assertEqual(None, node.render_end())

    node = nodes.SelfClosingHtmlNode('div')
    self.assertEqual(None, node.render_end())

