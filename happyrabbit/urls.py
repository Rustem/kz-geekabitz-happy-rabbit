"""happyrabbit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

import happyrabbit.hr_user.views

urlpatterns = [
    path('', happyrabbit.hr_user.views.MainPageView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('registration/', happyrabbit.hr_user.views.UserRegistrationView.as_view(), name='registration'),
    path('login/', happyrabbit.hr_user.views.UserLoginView.as_view(), name='login'),
    path('logout/', happyrabbit.hr_user.views.UserLogoutView.as_view(), name='logout'),
    path('onboarding/', happyrabbit.hr_user.views.OnBoardingView.as_view(), name='onboarding'),
    path('profile/', happyrabbit.hr_user.views.ProfileView.as_view(), name='profile')
    path('user/', include('happyrabbit.hr_user.urls')),
]
