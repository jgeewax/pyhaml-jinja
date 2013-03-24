import unittest2

from pyhaml_jinja import nodes
from pyhaml_jinja.parser import Parser


class TestParser(unittest2.TestCase):

  def test_parser_stores_source_text(self):
    parser = Parser('%div')
    self.assertEqual('%div', parser.source)

  def test_parser_builds_tree_on_init(self):
    parser = Parser('')
    self.assertIsInstance(parser.tree, nodes.Node)

