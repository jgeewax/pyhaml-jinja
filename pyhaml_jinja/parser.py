import re

from pyhaml_jinja.errors import TemplateIndentationError, TemplateSyntaxError
from pyhaml_jinja import nodes
#from nodes import Node, EmptyNode, HtmlNode, JinjaNode, TextNode


class Parser(object):
  """Responsible for reading a chunk of text and turnig it into a Node tree."""

  LINE_CONTINUATION = '\\' # Backslash for line continuations.
  LINE_COMMENT = ';' # Color for line comments.
  HTML_TAG_PREFIX = '%' # Haml standard is to use % to start HTML tags.
  JINJA_TAG_PREFIX = '-' # Use hypens to start Jinja code.

  def __init__(self, source, newline_string=None, indent_string=None):
    self.source = source
    self.newline_string = newline_string or ''
    self.indent_string = indent_string or ''
    self.tree = self.build_tree(source)

  def render(self):
    # Since the root node has no indentation, kick off the indentation level
    # at -1.
    lines = self.tree.render_lines(indent_string=self.indent_string,
                                   indent_level=-1)
    return self.newline_string.join(lines)

  @classmethod
  def parse_line(cls, line):
    """Parse a given line into a Node object.
    
    This method doesn't care about indentation, so line should be stripped
    of whitespace beforehand.
    """
    if not line:
      return nodes.EmptyNode()

    if line[0] in (cls.HTML_TAG_PREFIX, '.', '#'):
      return nodes.HtmlNode.from_haml(line)
    elif line[0] in cls.JINJA_TAG_PREFIX:
      return nodes.JinjaNode.from_haml(line)
    else:
      return nodes.TextNode(line)

  @classmethod
  def build_tree(cls, source_text):
    source_lines = cls.get_source_lines(source_text)

    root = nodes.Node()
    indent_stack = [-1]
    node_stack = [root]

    for line_number, line in enumerate(source_lines):

      try:
        node = cls.parse_line(line.strip())
      except Exception, e:
        raise TemplateSyntaxError(e.message, line_number)
      
      if isinstance(node, nodes.EmptyNode):
        node_stack[-1].add_child(node)
        continue

      try:
        indent = cls.get_indent_level(line)
      except Exception, e:
        raise TemplateIndentationError(e.message, line_number)

      if indent > indent_stack[-1]:
        indent_stack.append(indent)
      
      else:
        while indent < indent_stack[-1]:
          indent_stack.pop()
          node_stack.pop()

        node_stack.pop()
      
      if indent != indent_stack[-1]:
        raise TemplateIndentationError(
            'Unindent does not match any outer indentation level!', line_number)

      parent_node = node_stack[-1]
      
      # If children aren't allowed and we're indenting, throw an error.
      if not parent_node.children_allowed():
        raise TemplateSyntaxError(
            'Node of type %s cannot have children.' % type(node_stack[-1]),
            line_number)

      # Insert the child as always and move down the tree.
      parent_node.add_child(node)
      node_stack.append(node)

    return root

  @classmethod
  def get_indent_level(cls, line):
    """Given a line, determine how far indented it is."""
    indent = 0
    match = re.match(r'^(?P<whitespace>\s+)', line)
    if match:
      whitespace = match.group('whitespace')
      if ' ' in whitespace and '\t' in whitespace:
        raise ValueError('You cannot mix tabs and spaces!')

      indent = len(whitespace)
    return indent

  @classmethod
  def get_source_lines(cls, source_text):
    """Takes a chunk of text and parses it into a list of lines.
    
    This method is also responsible for merging continued-lines into a single
    line, stripping comments, and all sorts of other pre-processing.
    """

    source_lines = (source_text or '').rstrip().split('\n')
    lines = []
    line_builder = []

    for n, line in enumerate(source_lines):
      line = line.rstrip() # Remove trailing whitespace.

      # Make sure to handle line-continuations.
      # If the current line ends in a continuation, strip and append to the
      # builder.
      if line.endswith(cls.LINE_CONTINUATION):
        line_builder.append(line[:-1].strip())

      # If the line *doesn't* end in a continuation, but we have data in the
      # builder, wrap things up.
      elif line_builder:
        # Append the current line to the builder.
        line_builder.append(line.strip())

        # Append the 'built' line.
        lines.append(' '.join(line_builder))

        # Append blank lines for debugging.
        lines.extend(['']*(len(line_builder)-1))

        # Reset the builder.
        line_builder = []

      else:
        lines.append(line)

    return lines

