import json
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.template.loader import render_to_string


class Chat(models.Model):
    name = models.CharField(max_length=255, unique=False, blank=False)
    topic = models.CharField(max_length=255, unique=False, blank=True)
    participants = models.ManyToManyField(User)
    last_message_time = models.DateTimeField(null=True, blank=True, db_index=True)
    last_message_sender = models.ForeignKey(User, null=True, related_name='last_sender')

    def __str__(self):
        return self.name

    def get_user_list(self):
        return self.participants.all().order_by('username')


class Message(models.Model):
    text = models.TextField()
    sender = models.ForeignKey(User)
    thread = models.ForeignKey(Chat)
    datetime = models.DateTimeField(auto_now_add=True, db_index=True)

    # def get_html(self, style=''):
    #     return render_to_string('chat/message.html', {'message': self, 'style': style})

    def get_json_string(self):
        if self.sender.userprofile.profile_image:
            photo_url = self.sender.userprofile.profile_image.url
        else:
            photo_url = "/media/images/default.jpg"
        return json.dumps({
            'type': 'M',
            'username': self.sender.username,
            'photo': photo_url,
            'message': self.text
        })
    #
    # def get_self_html(self):
    #     return self.get_html(style='alert-success')
    #
    # def get_other_html(self):
    #     return self.get_html(style='alert-info')


def update_last_message(message):
    Chat.objects.filter(id=message.thread.id).update(
        last_message_time=message.datetime, last_message_sender=message.sender)
