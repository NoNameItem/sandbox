from django.db import models

# Create your models here.


class Bot(models.Model):
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    desc = models.TextField()
    token = models.CharField(max_length=100)


class Parameter(models.Model):
    code = models.CharField(max_length=30)
    desc = models.TextField()
    bot = models.ForeignKey(Bot)
    value = models.TextField()


class CommonTriggers(models.Model):
    trigger = models.CharField(max_length=100, primary_key=True)
    type = models.CharField(max_length=100)


class CommonReactions(models.Model):
    trigger_type = models.CharField(max_length=100)
    response = models.TextField()
