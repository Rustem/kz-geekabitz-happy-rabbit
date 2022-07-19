from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm

from happyrabbit.abc.external_account import EXTERNAL_SERVICE_CHOICES, LANGUAGE_CODE_CHOICES
from happyrabbit.hr_user.models import UserProfile, Account, ChildModel


class ReadOnlyForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_readonly()

    def set_readonly(self):
        for field in self.fields:
            self.fields[field].required = False
            self.fields[field].widget.attrs['disabled'] = 'disabled'
            self.fields[field].required = False


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class UserLoginForm(AuthenticationForm):
    pass


class UserProfileForm(ReadOnlyForm):
    language_code = forms.ChoiceField(widget=forms.Select(
        attrs={
            'class': 'form-select',
        },
    ),
        choices=LANGUAGE_CODE_CHOICES)

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'language_code', 'username',)


class AccountUpdateForm(ReadOnlyForm):
    external_service = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select',},),
                                         choices=EXTERNAL_SERVICE_CHOICES)

    class Meta:
        model = Account
        fields = ('external_service',)


class ChildUpdateForm(ModelForm):
    class Meta:
        model = ChildModel
        fields = ('name', 'age',)
