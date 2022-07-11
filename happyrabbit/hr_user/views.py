from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .forms import UserRegisterForm, UserLoginForm, AccountForm, ChildForm, UserProfileForm
from django.views.generic.edit import CreateView, FormView

from .models import Account, UserProfile, Child

from django.conf import settings

from happyrabbit.hr_user.auth.service import AuthService

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
    form_class = UserRegisterForm
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

        account_form = AccountForm()
        user_profile_form = UserProfileForm()
        child_form = ChildForm()
        message = ''
        return render(request, self.template_name, context={'account_form': account_form, 'child_form': child_form,
                                                            'user_profile_form': user_profile_form, 'message': message})

    def post(self, request):
        account_form = AccountForm(request.POST)
        user_profile_form = UserProfileForm(request.POST)
        child_form = ChildForm(request.POST)
        if all([account_form.is_valid(), user_profile_form.is_valid(), child_form.is_valid()]):
            account = account_form.save(commit=False)
            account.user = request.user
            account.save()

            user_profile = user_profile_form.save(commit=False)
            user_profile.account = account
            user_profile.save(force_insert=True)

            child = child_form.save(commit=False)
            child.guardian_id = request.user
            child.save()

            return redirect('profile')

        message = "Invalid Data"
        return render(request, self.template_name, context={'account_form': account_form, 'child_form': child_form,
                                                            'user_profile_form': user_profile_form, 'message': message})


class UserProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile.html'

    def get(self, request):
        if request.user.is_authenticated is False:
            return redirect('home')
        accounts = Account.objects.filter(user=request.user).all()
        user_profiles = UserProfile.objects.filter(account__in=accounts).all()
        childs = Child.objects.filter(guardian_id=request.user).all()

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
        kwargs['bot_deeplink'] = self._generate_deeplink(kwargs['account_id'])
        return kwargs

    def _generate_deeplink(self, account_id: int) -> str:
        auth_token = self.auth_service.get_auth_token(account_id)
        return f'http://t.me/{TELEGRAM_USERNAME}?start={auth_token.get_key()}'

