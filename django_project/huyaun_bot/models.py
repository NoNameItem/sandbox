from django.db import models

# Create your models here.


class Probability(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    value = models.IntegerField()


class LastWord(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    word = models.CharField(max_length=300)
    dt = models.DateTimeField()


class Exceptions(models.Model):
    key = models.CharField(max_length=300, primary_key=True)
    val = models.CharField(max_length=300, null=True)


class Timeout(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    value = models.IntegerField()
