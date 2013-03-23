import unittest2

from pyhaml_jinja.parser import Parser


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

