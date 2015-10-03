from django import forms
from chat.models import Chat
from chat.utils import get_private_chats

__author__ = 'nonameitem'


class ChatForm(forms.ModelForm):

    class Meta:
        model = Chat
        fields = ('name', 'topic', 'participants')
        widgets = {
            'participants': forms.SelectMultiple(attrs={'title': 'Select users'})
        }


class PrivateChatForm(forms.ModelForm):

    class Meta:
        model = Chat
        fields = ('name', 'topic')


def get_merge_form(user, other):
    chats = get_private_chats(user, other)
    choices = []
    for ch in chats:
        choices.append(ch.get_choice())

    class MergePrivateChatsForm(forms.Form):
        new_title = forms.CharField(max_length=255, initial="{0} <--> {1}".format(user.username, other.username))
        new_topic = forms.CharField(max_length=255, required=False)
        chats = forms.TypedMultipleChoiceField(coerce=lambda x: Chat.objects.get(id=x), choices=choices)

        def clean_chats(self):
            clean_data = self.cleaned_data['chats']
            if len(clean_data) < 2:
                raise forms.ValidationError('Please, select at least 2 chats')
            return clean_data

    return MergePrivateChatsForm
