# http://djangosnippets.org/snippets/1213/

from django import template
from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter


register = template.Library()


class CodeNode(template.Node):
    def __init__(self, lang, code):
        self.lang = lang
        self.nodelist = code
    
    def render(self, context):
        try:
            language = template.Variable(self.lang).resolve(context)
        except:
            language = self.lang
        code = self.nodelist.render(context)
        try:
            lexer = lexers.get_lexer_by_name(language)
        except:
            try:
                lexer = lexers.guess_lexer(code)
            except:
                lexer = lexers.PythonLexer()
        return highlight(code, lexer, HtmlFormatter(linenos='table'))


@register.tag(name='code')
def do_code(parser,token):
    code = token.split_contents()[-1]
    nodelist = parser.parse(('endcode',))
    parser.delete_first_token()
    return CodeNode(code,nodelist)

