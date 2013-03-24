import unittest2

from pyhaml_jinja.parser import Parser


class TestParserGetIndentLevel(unittest2.TestCase):

  def test_empty(self):
    self.assertEqual(0, Parser.get_indent_level(''))

  def test_no_indentation(self):
    self.assertEqual(0, Parser.get_indent_level('%div'))

  def test_normal(self):
    self.assertEqual(4, Parser.get_indent_level(4 * ' ' + '%div'))

  def test_whitespace_only(self):
    # get_source_lines should strip these, but get_indent_level respects
    # whitespace-only lines.
    self.assertEqual(4, Parser.get_indent_level('    '))

  def test_mixed_tabs_and_spaces_raises_error(self):
    with self.assertRaises(ValueError):
      Parser.get_indent_level('  \t  %div')

