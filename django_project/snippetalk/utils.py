import re

from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments import highlight as p_highlight


LEXERS = {item[0]: item[1][0] for item in get_all_lexers()}
LANGUAGE_CHOICES = tuple(zip(range(1, len(LEXERS)+1), sorted(LEXERS.keys())))
LANG_JS = [{'id': i[0], 'text': i[1]} for i in LANGUAGE_CHOICES]
PLAIN_TEXT = list(filter(lambda x: x[1] == 'Text only', LANGUAGE_CHOICES))[0][0]
SPACES = re.compile(r'(  +)')
EMPTY = re.compile(r'(<span.*?>)(</span>)')


class HtmlListFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        # yield 0, '<ol>'
        for i, t in source:
            if i == 1:
                space_escaped = \
                    SPACES.sub(lambda x: x.group(0).replace(' ', '&nbsp;'), t)
                t = '<li><div class="codeline">{0}</div></li>'.format(space_escaped if
                                                                      space_escaped != '\n'
                                                                      else '&nbsp')
            yield i, t
        # yield 0, '</ol>'


def highlight(code, lang):
    lexer = get_lexer_by_name(LEXERS[lang])
    return p_highlight(code, lexer, HtmlListFormatter())
