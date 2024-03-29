from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AccountUpdateForm, ChildUpdateForm
from django.views.generic.edit import CreateView

from .models import Account, UserProfile, ChildModel

from django.conf import settings

from tgbot.service.auth import AuthService

TELEGRAM_USERNAME = settings.TELEGRAM_USERNAME


class MainPageView(View):
    template_name = 'main.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('profile')
        return render(request, self.template_name)


class UserRegistrationView(SuccessMessageMixin, CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')
    form_class = UserRegistrationForm
    success_message = "Your profile was created successfully"

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)


class UserLoginView(View):
    template_name = 'users/login.html'
    form_class = UserLoginForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('profile')
        form = self.form_class()
        message = ''

        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)

                return redirect('profile')
        message = 'Login failed!'
        return render(request, self.template_name, context={'form': form, 'message': message})


class UserLogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect('home')


class UserOnBoardingView(View):
    template_name = 'users/onboarding.html'

    def get(self, request):
        child_form = ChildUpdateForm()
        message = ''
        return render(request, self.template_name, context={'child_form': child_form, 'message': message})

    def post(self, request):
        child_form = ChildUpdateForm(request.POST)
        if child_form.is_valid():
            child = child_form.save(commit=False)
            child.guardian = request.user
            child.save()

            return redirect('profile')

        message = "Invalid Data"
        return render(request, self.template_name, context={'child_form': child_form, 'message': message})


class UserProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile.html'

    def get(self, request):
        if request.user.is_authenticated is False:
            return redirect('home')
        accounts = Account.objects.filter(user=request.user).all()
        user_profiles = UserProfile.objects.filter(account__in=accounts).all()
        childs = ChildModel.objects.filter(guardian_id=request.user).all()

        context = {
            'accounts': accounts,
            'user_profiles': user_profiles,
            'childs': childs
        }
        return render(request, self.template_name, context=context)


class AuthDeepLinkView(LoginRequiredMixin, TemplateView):
    template_name = 'hr_user/deep_link.html'

    auth_service: AuthService

    def __init__(self, **kwargs):
        super().__init__()
        self.auth_service = AuthService()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['bot_deeplink'] = self._generate_deeplink(self.request.user, kwargs['account_id'])
        return kwargs

    def _generate_deeplink(self, user, account_id: int) -> str:
        account = self.auth_service.link_user_to_account(user, account_id)
        auth_token = self.auth_service.get_auth_token(user, account_id)
        return f'http://t.me/{TELEGRAM_USERNAME}?start={auth_token.get_key()}'

