import unittest2

from pyhaml_jinja.renderer import Renderer


class TestFullExample(unittest2.TestCase):

  def test_full_example(self):
    with open('tests/full_example.haml', 'r') as source_haml:
      renderer = Renderer(source_haml.read(), '\n', '  ')

    rendered_html = renderer.render()

    with open('tests/full_example.html', 'r') as expected_html:
      expected_html = expected_html.read().strip()

    self.maxDiff = None
    self.assertMultiLineEqual(expected_html, rendered_html)

