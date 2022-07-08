from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .abstract import ExternalUserProfile, ExternalAccount, ExternalSession
from .enums import EXTERNAL_SERVICE_CHOICES

import datetime
from django.utils import timezone


class Account(ExternalAccount, models.Model):

    account_id = models.IntegerField(primary_key=True)
    external_service = models.CharField(max_length=200, choices=EXTERNAL_SERVICE_CHOICES)
    external_user_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_username(self):
        return self.userprofile.username

    def get_external_service(self) -> str:
        return self.external_service

    def get_external_user_id(self) -> int:
        return self.external_user_id

    def get_external_profile(self) -> ExternalUserProfile:
        # TODO handle DOESNOTEXIST
        return self.userprofile


class UserProfile(models.Model, ExternalUserProfile):

    user_profile_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    language_code = models.CharField(max_length=2, blank=True)
    username = models.CharField(max_length=200, null=False)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    def get_first_name(self) -> str:
        return self.first_name

    def get_last_name(self) -> str:
        return self.last_name

    def get_language_code(self) -> str:
        return self.language_code

    def get_username(self) -> str:
        return self.username


class Child(models.Model):
    child_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    carrots = models.IntegerField(default=0)
    guardian_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if self.age > 18:
            raise ValidationError("Child must be younger than 18!")

    def __str__(self):
        return f'{self.name} - {self.age} years old'


class Session(ExternalSession, models.Model):

    session_id = models.IntegerField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    date_logged_in = models.DateTimeField("date logged in", default=timezone.now)

    def get_session_id(self) -> str:
        pass

    def get_account(self) -> ExternalAccount:
        return self.account

    def get_date_logged_in(self) -> datetime.datetime:
        return self.date_logged_in

    def get_username(self) -> str:
        return self.account is not None and self.account.get_username()

    def is_active(self):
        raise NotImplementedError("not implemented")

    def is_admin(self):
        raise NotImplementedError("not implemented")

    def is_onboarded(self):
        raise NotImplementedError("not implemented")
