from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import re_path, path

import happyrabbit
from . import views

urlpatterns = [
    path('category/create/', happyrabbit.activity.views.CategoryCreateView.as_view(), name='category_create'),
    path('activity/create/', happyrabbit.activity.views.ActivityCreateView.as_view(), name='activity_create'),
    path('activity/view/', happyrabbit.activity.views.ActivityView.as_view(), name='activity_view'),
    path('rewardrule/create/', happyrabbit.activity.views.RewardRuleCreateView.as_view(), name='reward_rule_create'),
]