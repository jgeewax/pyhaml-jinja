import unittest2

from pyhaml_jinja.errors import TemplateIndentationError
from pyhaml_jinja.parser import Parser


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

