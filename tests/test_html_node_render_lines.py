import unittest2

from pyhaml_jinja import nodes


class TestNodeRenderLines(unittest2.TestCase):

  def test_simple(self):
    node = nodes.HtmlNode('div')
    lines = node.render_lines()
    self.assertEqual(['<div>', '</div>'], lines)

  def test_simple_content(self):
    node = nodes.HtmlNode('div')
    node.add_child(nodes.TextNode('content'))
    lines = node.render_lines()
    self.assertEqual(['<div>', 'content', '</div>'], lines)

  def test_nested(self):
    parent = nodes.HtmlNode('div')
    child = nodes.HtmlNode('p')
    text = nodes.TextNode('content')
    parent.add_child(child)
    child.add_child(text)

    lines = parent.render_lines()
    self.assertEqual(['<div>', '<p>', 'content', '</p>', '</div>'], lines)

  def test_multiple_trees(self):
    parent = nodes.HtmlNode('div')
    child1 = nodes.HtmlNode('p')
    child2 = nodes.HtmlNode('span')
    child1.add_child(nodes.TextNode('ptext'))
    child2.add_child(nodes.TextNode('spantext'))
    parent.add_child(child1)
    parent.add_child(child2)

    lines = parent.render_lines()
    self.assertEqual(['<div>', '<p>', 'ptext', '</p>', '<span>', 'spantext',
                      '</span>', '</div>'], lines)
  def test_render_condensed_node(self):
    parent = nodes.HtmlNode('div', condensed=True)
    child = nodes.HtmlNode('p')
    text = nodes.TextNode('content')
    parent.add_child(child)
    child.add_child(text)
    lines = parent.render_lines()
    self.assertEqual(['<div><p>', 'content', '</p></div>'], lines)

  def test_render_condensed_node_child(self):
    parent = nodes.HtmlNode('div')
    child1 = nodes.HtmlNode('p', condensed=True)
    child2 = nodes.HtmlNode('span')
    child1.add_child(nodes.TextNode('ptext'))
    child2.add_child(nodes.TextNode('spantext'))
    parent.add_child(child1)
    parent.add_child(child2)

    lines = parent.render_lines()
    self.assertEqual(['<div>', '<p>ptext</p>', '<span>', 'spantext',
                      '</span>', '</div>'], lines)

  def test_render_condensed_single_node(self):
    node = nodes.HtmlNode('div', condensed=True)
    self.assertEqual(['<div></div>'], node.render_lines())
