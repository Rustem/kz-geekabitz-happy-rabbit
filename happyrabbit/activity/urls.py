from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import re_path, path

import happyrabbit
from . import views

urlpatterns = [
    path('category/create/', happyrabbit.activity.views.CategoryCreateView.as_view(), name='category-create'),
    path('activity/create/', happyrabbit.activity.views.ActivityCreateView.as_view(), name='activity-create'),
    path('activity/view/', happyrabbit.activity.views.ActivityListView.as_view(), name='activity-view'),
    path('reward-rule/create/', happyrabbit.activity.views.RewardRuleCreateView.as_view(), name='reward-rule-create'),
]