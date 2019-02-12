from django import forms
from models import Message

class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        exclude = ('created_at',)
