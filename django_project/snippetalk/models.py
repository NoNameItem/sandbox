from django.contrib.auth.models import User
from django.db import models
import snippetalk.utils as u


class Snippet(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    public = models.IntegerField(default=True, choices=((1, 'Public'), (2, 'Private')),
                                 verbose_name="Publicity")
    name = models.CharField(max_length=100, default="Untitled")
    description = models.TextField(blank=True)
    language = models.IntegerField(choices=u.LANGUAGE_CHOICES, default=u.PLAIN_TEXT)
    code = models.TextField()

    @property
    def highlighted(self):
        return u.highlight(self.code, self.get_language_display())


class Comment(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    language = models.IntegerField(choices=u.LANGUAGE_CHOICES, default=u.PLAIN_TEXT)
    code = models.TextField(blank=True)

