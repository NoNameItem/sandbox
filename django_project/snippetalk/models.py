from tempfile import TemporaryFile

from django.contrib.auth.models import User
from django.db import models
from django.template import Template, Context, loader
from django.template.loader import render_to_string

import snippetalk.utils as u


class Snippet(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    public = models.IntegerField(default=1, choices=((1, 'Public'), (2, 'Private')),
                                 verbose_name="Publicity")
    name = models.CharField(max_length=100, default="Untitled")
    description = models.TextField(blank=True)
    language = models.IntegerField(choices=u.LANGUAGE_CHOICES, default=u.PLAIN_TEXT)
    code = models.TextField()

    @property
    def highlighted(self):
        return u.highlight(self.code, self.get_language_display())

    @property
    def modified_str(self):
        t = Template('{{ date }}')
        return t.render(Context({'date': self.modified}))

    @property
    def top_level_comments(self):
        return self.comments.filter(parent__isnull=True)

    def get_file(self):
        filename = u.get_filename(self.name, self.get_language_display())
        f = open(filename, mode='wt')
        f.write(self.code)
        f.close()
        return filename


class Comment(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    to_snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, default=None, related_name='answers')
    snippets = models.ManyToManyField(Snippet, default=None, related_name='mentions')

    def render(self):
        return render_to_string('snippetalk/comment.html', {'comm': self})
