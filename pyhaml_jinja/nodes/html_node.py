"""Nodes that render into HTML tags."""

import re

from pyhaml_jinja.nodes.node import Node
from pyhaml_jinja.nodes.childless_node import ChildlessNode
from pyhaml_jinja.nodes.text_node import TextNode, PreformattedTextNode


__all__ = ['HtmlNode', 'SelfClosingHtmlNode', 'HtmlCommentNode']


class HtmlNode(Node):
  """Represents a standard HTML node with a tag, attributes, and children."""

  TAG_REGEX = re.compile(
      r'^'  # Start of the line
      r'%'  # % is required
      r'(?P<tag>\w+)'  # tag name is required
      r'(?P<shortcut_attrs>[\.#][^()]+?)?'  # .cls1.cls2#id is optional
      r'(?P<attrs>\(.+?\))?'  # (a="1", b="2") are optional
      r'(?P<content>\s+.+)?'  # Inline-content is optional
      r'$'  # End of the line
  )

  SELF_CLOSING_TAGS = ['br', 'hr', 'img', 'input', 'link', 'meta']

  def __init__(self, tag, attributes=None):
    self.tag = tag
    self.attributes = attributes or {}
    super(HtmlNode, self).__init__()

  def add_attribute(self, key, value):
    """Safely add an attribute to this node.

    Raises an exception if you try to clobber a variable (not class).
    If you add an extra class, appends it correctly to the existing class.
    """
    if key == 'class':
      # Class is a special one, which can be defined multiple times (and
      # should be appended with spaces in-between).
      value = self.attributes.get('class', '') + ' ' + value

    elif key in self.attributes:
      raise KeyError(
          'Attribute %s already defined on node %s!' % (key, self))

    self.attributes[key] = value.strip()

  @classmethod
  def from_haml(cls, haml):
    """Given a line of HAML markup, return the correct HtmlNode."""

    # You can omit the % if and only if the line starts with a '.' or '#'.
    if haml and not haml.startswith('%') and haml[0] in ('.', '#'):
      haml = '%div' + haml

    # Handle nested tags on the same line by splitting into chunks and
    # processing each line separately, then appending down the tree.
    if re.match(r'^[^\s]+:\s+', haml):
      root = None
      parent = None

      for line in re.split(r':\s+', haml):
        # This needs to be here to avoid circular imports.
        from pyhaml_jinja.parser import Parser
        child = Parser.parse_line(line)

        if not root:
          root = child

        if parent:
          # This may raise an exception if it turns out that parent is not
          # permitted to have children.
          parent.add_child(child)

        parent = child

      return root

    match = cls.TAG_REGEX.match(haml)
    if not match:
      raise ValueError('Text did not match %s' % cls.TAG_REGEX.pattern)

    # Create the node with the proper tag
    tag = match.group('tag')

    if tag in cls.SELF_CLOSING_TAGS:
      node = SelfClosingHtmlNode(tag=tag)
    else:
      node = cls(tag=tag)

    # Handle shortcut attributes ('.cls#id')
    shortcut_attrs = match.group('shortcut_attrs')
    if shortcut_attrs:
      # Splits into ['.', 'cls', '#', 'id']
      parts = re.split(r'([\.#])', shortcut_attrs)[1:]
      # Zips together into [('.', 'cls'), ('#', 'id')]
      parts = zip(parts[0::2], parts[1::2])

      for prefix, value in parts:
        if prefix == '.':
          node.add_attribute('class', value)
        elif prefix == '#':
          node.add_attribute('id', value)

    # Handle regular attributes ('(a="1", b="2")')
    attrs = match.group('attrs')
    if attrs:
      # Splits apart by commas, but not commas within quotes.
      attr_pairs = re.compile(r'(?:[^,"]|"[^"]*")+').findall(attrs[1:-1])
      if any(_.count('"') != 2 for _ in attr_pairs):
        raise ValueError('Mismatched quotes (or missing comma) in attributes!')

      # Breaks pair strings into [(key, value), ...].
      attr_pairs = [pair.strip().split('=') for pair in attr_pairs]
      for (key, value) in attr_pairs:
        node.add_attribute(key, value[1:-1])

    # Handle in-line content.
    content = (match.group('content') or '').strip()
    if content:
      if not node.children_allowed():
        raise ValueError('Inline content not permitted on %s' % node)
      node.add_child(TextNode(content))

    return node

  @classmethod
  def _render_attributes(cls, attributes):
    """Given a dictionary, return an HTML-style attribute string."""
    items = (attributes or {}).iteritems()
    return ' '.join('%s="%s"' % (k, v) for (k, v) in items)

  def render_attributes(self):
    """Convenience instance-method for rendering the node's attributes."""
    return self._render_attributes(self.attributes)

  def render_start(self):
    tag = self.tag
    attributes = self.render_attributes()
    start = '<%s>' % ' '.join([tag, attributes]).strip()

    # Special case for our first child being a PreformattedTextNode.
    if self.has_children():
      first_child = self.get_children()[0]
      if isinstance(first_child, PreformattedTextNode):
        start += first_child.render_start(force=True)

    return start

  def render_end(self):
    return '</{tag}>'.format(tag=self.tag)


class SelfClosingHtmlNode(HtmlNode, ChildlessNode):
  """An HtmlNode that closes itself (<hr />)."""

  def render_start(self):
    tag = self.tag
    attributes = self.render_attributes()
    return '<%s />' % ' '.join([tag, attributes]).strip()

  def render_end(self):
    return None


class HtmlCommentNode(TextNode, ChildlessNode):
  """An Html Comment node."""

  def render_start(self):
    start = super(HtmlCommentNode, self).render_start()
    return '<!-- %s -->' % start.strip()

