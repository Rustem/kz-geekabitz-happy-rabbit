from django.contrib.auth import authenticate, login
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView

from .forms import UserRegisterForm, UserLoginForm, AccountForm, ChildForm, UserProfileForm
from django.views.generic.edit import CreateView, FormView

from .models import Account, UserProfile, Child


class MainPageView(TemplateView):
    template_name = 'main.html'


class UserRegistrationView(SuccessMessageMixin, CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"


class UserLoginView(View):
    template_name = 'users/login.html'
    form_class = UserLoginForm

    def get(self, request):
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

                return redirect('home')
        message = 'Login failed!'
        return render(request, self.template_name, context={'form': form, 'message': message})


class OnBoardingView(View):
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
            account_form.external_user_id = 123
            account_form.user = request.user
            account = account_form.save(commit=True)

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


class ProfileView(View):
    template_name = 'users/profile.html'

    def get(self, request):
        accounts = Account.objects.filter(user=request.user).all()
        user_profiles = UserProfile.objects.filter(account__in=accounts).all()
        childs = Child.objects.filter(guardian_id=request.user).all()

        context = {
            'accounts': accounts,
            'user_profiles': user_profiles,
            'childs': childs
        }
        return render(request, self.template_name, context=context)
