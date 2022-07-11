from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import re_path, path

import happyrabbit
from . import views

urlpatterns = [
    re_path(r'^auth/login/$', auth_views.LoginView.as_view(), name='auth-login'),
    re_path(r'^auth/deeplink/(?P<account_id>[0-9]+)/$', login_required(views.AuthDeepLinkView.as_view()), name='auth-deeplink'),
    path('registration/', happyrabbit.hr_user.views.UserRegistrationView.as_view(), name='registration'),
    path('login/', happyrabbit.hr_user.views.UserLoginView.as_view(), name='login'),
    path('logout/', happyrabbit.hr_user.views.UserLogoutView.as_view(), name='logout'),
    path('onboarding/', happyrabbit.hr_user.views.OnBoardingView.as_view(), name='onboarding'),
    path('profile/', happyrabbit.hr_user.views.ProfileView.as_view(), name='profile'),
]