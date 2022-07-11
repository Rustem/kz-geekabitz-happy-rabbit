from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^auth/login/$', auth_views.LoginView.as_view(), name='auth-login'),
    re_path(r'^auth/deeplink/(?P<account_id>[0-9]+)/$', login_required(views.AuthDeepLinkView.as_view()), name='auth-deeplink')
]