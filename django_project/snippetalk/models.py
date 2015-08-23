from django.contrib.auth.models import User
from django.db import models
from pygments import highlight
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.formatters import HtmlFormatter


LEXERS = {item[0]: item[1][0] for item in get_all_lexers()}
LANGUAGE_CHOICES = tuple(zip(range(len(LEXERS)), sorted(LEXERS.keys())))
PLAIN_TEXT = list(filter(lambda x: x[1] == 'Text only', LANGUAGE_CHOICES))[0][0]


class Snippet(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=100, default="Untitled")
    language = models.IntegerField(choices=LANGUAGE_CHOICES, default=PLAIN_TEXT)
    code = models.TextField()

    @property
    def highlighted(self):
        lexer = get_lexer_by_name(LEXERS[self.get_language_display()])
        return highlight(self.code, lexer, HtmlFormatter)


class Comment(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    language = models.IntegerField(choices=LANGUAGE_CHOICES, default=PLAIN_TEXT)
    code = models.TextField(blank=True)
