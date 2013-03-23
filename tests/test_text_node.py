import unittest2

from pyhaml_jinja import nodes


class TestTextNode(unittest2.TestCase):

  def test_properly_stores_data(self):
    node = nodes.TextNode('data')
    self.assertEqual('data', node.data)

  def test_requires_data_at_instantiation(self):
    with self.assertRaises(Exception):
      node = nodes.TextNode()

  def test_render_start_shows_just_data(self):
    node = nodes.TextNode('data')
    self.assertEqual('data', node.render_start())

  def test_render_end_is_None(self):
    node = nodes.TextNode('data')
    self.assertEqual(None, node.render_end())

