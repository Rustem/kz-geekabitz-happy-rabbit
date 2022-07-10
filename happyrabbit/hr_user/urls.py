from django.contrib.auth.decorators import login_required
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^auth/(?P<account_id>[0-9]+)/$', login_required(views.AuthDeepLinkView.as_view()), name='auth')
]