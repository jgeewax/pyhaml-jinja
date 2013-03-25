import unittest2

from pyhaml_jinja.errors import TemplateSyntaxError
from pyhaml_jinja.parser import Parser


class TestParserGetSourceLines(unittest2.TestCase):

  def test_empty(self):
    self.assertEqual([''], Parser.get_source_lines(''))
    self.assertEqual([''], Parser.get_source_lines(None))
    self.assertEqual([''], Parser.get_source_lines('\n'))

  def test_basic(self):
    source = (
        '%div\n'
        '  text\n'
        '%p\n'
        '  %p\n'
        '    nested-text\n'
        )

    lines = Parser.get_source_lines(source)
    self.assertEqual(['%div', '  text', '%p', '  %p', '    nested-text'],
                     lines)

  def test_trailing_whitespace(self):
    source = (
        '%div' + '     '  # 5 whitespace characters at the end.
        )
    lines = Parser.get_source_lines(source)
    self.assertEqual(['%div'], lines)

  def test_comment(self):
    source = (
        '%div\n'
        '; comment\n'
        '  text\n'
        )
    lines = Parser.get_source_lines(source)
    self.assertEqual(3, len(lines))
    self.assertEqual(['%div', '', '  text'], lines)

  def test_line_continuation(self):
    source = (
        '%div(a="1", \\\n'
        '     b="2")\n'
        '  text\n'
        )
    lines = Parser.get_source_lines(source)
    self.assertEqual(3, len(lines))
    self.assertEqual(['%div(a="1", b="2")', '', '  text'], lines)

  def test_line_continuation_ending_prematurely(self):
    source = (
        '%div(a="1", \\ \n'
        )
    with self.assertRaises(TemplateSyntaxError):
      Parser.get_source_lines(source)

  def test_line_continuation_indented_properly(self):
    source = (
        '%div\n'
        '  %p(a="1", \\ \n'
        '     b="2")\n'
        '    Text\n'
        )
    lines = Parser.get_source_lines(source)
    self.assertEqual(['%div', '  %p(a="1", b="2")', '', '    Text'], lines)

  def test_jinja_variables(self):
    source = '#{var} #{var2}'
    lines = Parser.get_source_lines(source)
    self.assertEquals(['{{ var }} {{ var2 }}'], lines)

    source = '%hr(class="#{class}")'
    lines = Parser.get_source_lines(source)
    self.assertEqual(['%hr(class="{{ class }}")'], lines)

