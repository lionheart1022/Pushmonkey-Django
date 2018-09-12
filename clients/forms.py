from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from models import ClientProfile, ProfileImage
from website_clusters.models import Website, WebsiteIcon
from captcha.fields import ReCaptchaField
import os

class UserForm(forms.ModelForm):
    first_name = forms.CharField()
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput())
    captcha = ReCaptchaField(required = os.environ.get('RECAPTCHA_TESTING', 'False') != 'True')
    class Meta:
        model = User
        fields = ('first_name', 'email', 'password')

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError("The password and password confirmation must match")
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(username = email)
        except User.DoesNotExist:
            user = None
        if user:
            raise forms.ValidationError('This email is already taken. Have you forgotten your password? <a href="' + reverse('password_reset') + '">Click here</a>')
        return email


class ClientProfileForm(forms.ModelForm):
    website_name = forms.CharField(required = False)
    return_url = forms.CharField(required = False)
    website = forms.CharField(required = False)

    class Meta:
        model = ClientProfile
        fields = ('website_name', 'return_url', 'website', 'from_envato')

class ResendConfirmForm(forms.Form):
    email = forms.CharField()

class ProfileImageForm(forms.ModelForm):

    website_url = forms.CharField()
    website_name = forms.CharField()

    class Meta:
        model = ProfileImage
        fields = ('image', )

class UpdateProfileImageForm(forms.ModelForm):

    class Meta:
        model = ProfileImage
        fields = ('image', )  

class WebsiteIconForm(forms.ModelForm):

    class Meta:
        model = WebsiteIcon
        fields = ('image', )

class CustomiseForm(forms.Form):
    website_url = forms.URLField()
    website_name = forms.CharField()
    profile_id = forms.CharField(widget=forms.HiddenInput())

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label=("Email"), max_length = 100)

class WebsiteForm(forms.Form):
    agent = forms.EmailField(help_text="The email of the person who will manage the notifications for this website will receive an invitation email. If left blank, only the current account can send notifications.", required = False)
    icon = forms.ImageField()  
    website_name = forms.CharField()
    website_url = forms.URLField(help_text = "The full URL of your WordPress website where Push Monkey is installed. E.g. http://blog.getpushmonkey.com")

    def clean_agent(self):
        agent = self.cleaned_data.get('agent')
        websites = Website.objects.filter(agent__email = agent).count()
        if websites != 0:
            raise forms.ValidationError('The email of the Agent must be unique.')
        return agent