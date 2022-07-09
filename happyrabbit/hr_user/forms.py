from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm

from happyrabbit.hr_user.models import UserProfile, Account, Child


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']


class UserLoginForm(AuthenticationForm):
    pass


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'language_code', 'username',)


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ('external_service', 'external_user_id', 'user')


class ChildForm(ModelForm):
    class Meta:
        model = Child
        fields = ('name', 'age',)


class OnBoardingForm(ModelForm):
    pass
