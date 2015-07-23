from django import forms
from chat.models import Chat

__author__ = 'nonameitem'


class ChatForm(forms.ModelForm):

    class Meta:
        model = Chat
        fields = ('name', 'topic', 'participants')
        widgets = {
            'participants': forms.SelectMultiple(attrs={'class': 'selectpicker', 'title': 'Select users'})
        }


class PrivateChatForm(forms.ModelForm):

    class Meta:
        model = Chat
        fields = ('name', 'topic')
