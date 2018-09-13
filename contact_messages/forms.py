from django import forms
from models import Message
from captcha.fields import ReCaptchaField

class MessageForm(forms.ModelForm):

    captcha = ReCaptchaField()

    class Meta:
        model = Message
        exclude = ('created_at',)