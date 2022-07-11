from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm

from happyrabbit.hr_user.enums import EXTERNAL_SERVICE_CHOICES, LANGUAGE_CODE_CHOICES
from happyrabbit.hr_user.models import UserProfile, Account, Child


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']


class UserLoginForm(AuthenticationForm):
    pass


class UserProfileForm(ModelForm):
    language_code = forms.ChoiceField(widget=forms.Select(
        attrs={
            'class': 'form-select',
        },
    ),
        choices=LANGUAGE_CODE_CHOICES)

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'language_code', 'username',)


class AccountForm(ModelForm):
    external_service = forms.ChoiceField(widget=forms.Select(
        attrs={
            'class': 'form-select',
        },
    ),
        choices=EXTERNAL_SERVICE_CHOICES)

    class Meta:
        model = Account
        fields = ('external_service',)


class ChildForm(ModelForm):
    class Meta:
        model = Child
        fields = ('name', 'age',)


class OnBoardingForm(ModelForm):
    pass
