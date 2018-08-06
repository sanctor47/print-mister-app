from django import forms
from django.contrib.auth.models import User

from registration.forms import RegistrationForm

from .models import Client


class Email(forms.EmailField):
    def clean(self, value):
        super(Email, self).clean(value)
        try:
            User.objects.get(email=value)
            raise forms.ValidationError(
                "This email is already registered. Use the 'forgot password' link on the login page")
        except User.DoesNotExist:
            return value


class UserRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        fields = [
            #User.USERNAME_FIELD,
            'email',
            'password1',
            'password2'
        ]
        required_css_class = 'required'

    def save(self, commit=True):
        self.instance.username = self.cleaned_data['email']
        user = super(UserRegistrationForm, self).save(commit)
        user.save()
        Client.objects.create(user=user)
        return user


class ClientEditForm(forms.ModelForm):
    full_name = forms.CharField()
    favourite_colour = forms.CharField()

    class Meta:
        model = Client
        fields = ['full_name', 'favourite_colour']