import re

from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments import highlight as p_highlight


LEXERS = {item[0]: item[1][0] for item in get_all_lexers()}
LANGUAGE_CHOICES = tuple(zip(range(1, len(LEXERS)+1), sorted(LEXERS.keys())))
LANG_TO_EXT = {item[0]: item[2] if item[2] else ('*.txt',) for item in get_all_lexers()}

EXT_TO_LANG_CODE = {}
language_choice_revert = {i[1]: i[0] for i in LANGUAGE_CHOICES}
for k, v in LANG_TO_EXT.items():
    for ext in v:
        if ext.startswith('*'):
            ext = ext[1:]
        elif not ext.startswith('.'):
            ext = '.' + ext

        EXT_TO_LANG_CODE[ext] = language_choice_revert[k]

LANG_JS = [{'id': i[0], 'text': i[1]} for i in LANGUAGE_CHOICES]
PLAIN_TEXT = list(filter(lambda x: x[1] == 'Text only', LANGUAGE_CHOICES))[0][0]
SPACES = re.compile(r'(  +)')
EMPTY = re.compile(r'(<span.*?>)(</span>)')
FILENAME = re.compile(r'(?P<name>.+)(?P<ext>\..+)')


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


def get_filename(name, lang):
    return LANG_TO_EXT[lang][0].replace('*', '[snippetalk]' + name)


def parse_filename(filename):
    m = FILENAME.match(filename)
    return m.group('name'), EXT_TO_LANG_CODE.get(m.group('ext'), PLAIN_TEXT)
