import unittest2

from pyhaml_jinja.renderer import Renderer


class TestRenderer(unittest2.TestCase):
  def test_basic(self):
    source = (
        '%div\n'
        '  text\n'
        )
    renderer = Renderer(source)
    html = renderer.render()
    self.assertEqual('<div>text</div>', html)

  def test_with_newlines(self):
    source = (
        '%div\n'
        '  %p text\n'
        '  text2\n'
        )
    renderer = Renderer(source, newline_string='\n')
    html = renderer.render()
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
    renderer = Renderer(source, newline_string='\n', indent_string='  ')
    html = renderer.render()
    self.assertEqual((
      '<div>\n'
      '  <p>\n'
      '    text\n'
      '  </p>\n'
      '  text2\n'
      '</div>'
      ), html)

  def test_with_preformatted(self):
    source = (
        '%pre\n'
        '  |line1\n'
        '  |line2\n'
        )
    renderer = Renderer(source, newline_string='\n', indent_string='  ')
    html = renderer.render()
    self.assertEqual((
      '<pre>'
      'line1\n'
      'line2\n'
      '</pre>'), html)

