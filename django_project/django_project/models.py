import datetime
import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.related import OneToOneField


class UserProfile(models.Model):
    user = OneToOneField(User)

    SEX_CHOICES = (
        (0, "Female"),
        (1, "Male"),
        (2, "Undefined")
    )

    sex = models.IntegerField(choices=SEX_CHOICES, default=2)
    profile_image = models.ImageField(upload_to='images/', null=True)
    about = models.TextField(blank=True)

    def set_profile_image(self, f):
        filename = str(datetime.datetime.now()) + "-" + self.user.username + '.' + f.name.split('.')[-1]
        self.profile_image.delete()
        self.profile_image.save(filename, f)
        self.save()

    @property
    def image_url(self):
        return self.profile_image.url if self.profile_image else "/media/images/default.jpg"

    def __str__(self):
        return self.user.username
