from django import forms
from snippetalk.models import Snippet


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ('name', 'public', 'language', 'code', 'description')
        widgets = {
            'public': forms.RadioSelect()
        }

