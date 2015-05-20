# http://djangosnippets.org/snippets/1213/

from django import template
from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter


register = template.Library()


class CodeNode(template.Node):
    def __init__(self, lang, code, linenos):
        self.lang = lang
        self.nodelist = code
        self.linenos = linenos
    
    def render(self, context):
        try:
            language = template.Variable(self.lang).resolve(context)
        except:
            language = self.lang
        code = self.nodelist.render(context)
        try:
            linenos = template.Variable(self.linenos).resolve(context)
        except:
            linenos = self.linenos
        try:
            lexer = lexers.get_lexer_by_name(language)
        except:
            try:
                lexer = lexers.guess_lexer(code)
            except:
                lexer = lexers.PythonLexer()
        return highlight(code, lexer, HtmlFormatter(linenos=linenos))


@register.tag(name='code')
def do_code(parser, token):
    token_contents = token.split_contents()
    if len(token_contents) == 2:
        code = token_contents[1]
        linenos = 'table'
    elif len(token_contents) == 3:
        _, code, linenos = token_contents
    else:
        raise template.TemplateSyntaxError(
            "%r tag requires arguments" % token.contents.split()[0]
        )
    nodelist = parser.parse(('endcode',))
    parser.delete_first_token()
    return CodeNode(code, nodelist, linenos)
