from pyhaml_jinja.nodes.node import Node


__all__ = ['TextNode']


class TextNode(Node):

  """TextNodes can actually have children.
  
  If there are tags we don't understand, we shouldn't get in the way::
    
    {#$% if True %$#}
      %div
        content
    {#$% endif %$#}
  
  might be perfectly valid, and is technically a TextNode -> HtmlNode -> TextNode.
  """

  def __init__(self, data):
    self.data = data
    super(TextNode, self).__init__()

  def render_start(self):
    return self.data

