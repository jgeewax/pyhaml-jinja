from jinja2 import TemplateSyntaxError


__all__ = ['TemplateIndentationError', 'TemplateSyntaxError']


class TemplateIndentationError(TemplateSyntaxError):
  """Raised when a line's indentation has an error."""
  pass

