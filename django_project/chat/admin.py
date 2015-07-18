from django.contrib import admin

# Register your models here.
from chat.models import Chat, Message

admin.site.register(Chat)
admin.site.register(Message)
