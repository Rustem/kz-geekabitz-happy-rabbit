import binascii
import os
from typing import List

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.timezone import now

from happyrabbit.abc.errors import IllegalArgumentError
from happyrabbit.abc.external_account import ExternalUserProfile, ExternalAccount, ExternalSession, AuthToken
from happyrabbit.abc.external_account import EXTERNAL_SERVICE_CHOICES

import datetime
from django.utils import timezone

from happyrabbit.abc.family import Child, BaseChildren


class Account(ExternalAccount, models.Model):
    account_id = models.BigAutoField(primary_key=True)
    external_service = models.CharField(max_length=200, choices=EXTERNAL_SERVICE_CHOICES)
    external_user_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def get_username(self):
        return self.userprofile.username

    def get_external_service(self) -> str:
        return self.external_service

    def get_external_user_id(self) -> int:
        return self.external_user_id

    def get_external_profile(self) -> ExternalUserProfile:
        # TODO handle DOESNOTEXIST
        return self.userprofile

    def get_linked_user(self):
        return self.user

    def is_saved(self) -> bool:
        return not self._state.adding

    def is_linked_to_user(self, target_user) -> bool:
        if target_user is None:
            raise IllegalArgumentError("target_user is null")
        return self.get_linked_user() and self.get_linked_user() == target_user


class UserProfile(models.Model, ExternalUserProfile):
    user_profile_id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    language_code = models.CharField(max_length=2, blank=True)
    username = models.CharField(max_length=200, blank=True, null=False)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    def get_first_name(self) -> str:
        return self.first_name

    def get_last_name(self) -> str:
        return self.last_name

    def get_language_code(self) -> str:
        return self.language_code

    def get_username(self) -> str:
        return self.username


class ChildModel(Child, models.Model):
    child_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    carrots = models.IntegerField(default=0)
    guardian = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if self.age > 18:
            raise ValidationError("Child must be younger than 18!")

    def __str__(self):
        return f'{self.name} - {self.age} years old'

    def get_child_id(self) -> str:
        return self.child_id

    def get_name(self) -> str:
        return self.name

    def get_age(self) -> int:
        return self.age

    def get_carrots(self) -> int:
        return self.carrots

    def get_guardian(self):
        return self.guardian


class Children(BaseChildren):

    children: List[Child]
    index: int

    def __init__(self, children):
        if children is None:
            children = list()
        self.children = children
        self.index = 0

    def __next__(self) -> Child:
        try:
            kid = self.children[self.index]
        except IndexError:
            raise StopIteration

        self.index += 1
        return kid

    def get_child(self, child_idx: int) -> Child:
        if child_idx >= len(self.children):
            raise IndexError("list index out of range")
        return self.children[child_idx]

    def get_child_by_name(self, name: str) -> Child | None:
        return next(child for child in self.children
                    if child.get_name() == name)

    @property
    def family_size(self) -> int:
        return len(self.children)


class AuthTokenModel(AuthToken, models.Model):
    class Meta:
        db_table = "hr_user_auth_token"

    key = models.CharField(max_length=40, primary_key=True)
    created = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(AuthToken, self).save(*args, **kwargs)

    def get_key(self) -> str:
        return self.key

    def get_created(self) -> datetime.datetime:
        return self.created

    def is_expired(self) -> bool:
        return self.get_created() < now() - datetime.timedelta(
            hours=int(getattr(settings, 'HAPPY_RABBIT_AUTH_TOKEN_EXPIRATION_HOURS', '24')))

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()


class Session(ExternalSession, models.Model):
    session_id = models.CharField(primary_key=True, max_length=40)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    date_logged_in = models.DateTimeField("date logged in", default=timezone.now)
    auth_token = models.ForeignKey(AuthTokenModel, null=True, on_delete=models.SET_NULL)

    def get_session_id(self) -> str:
        return self.session_id

    def get_account(self) -> ExternalAccount:
        return self.account

    def get_date_logged_in(self) -> datetime.datetime:
        return self.date_logged_in

    def get_username(self) -> str:
        return self.account is not None and self.account.get_username()

    def get_login_date(self) -> datetime.datetime:
        return self.date_logged_in

    def get_auth_token(self) -> AuthToken:
        return self.auth_token

    def is_expired(self) -> bool:
        return not self.auth_token or self.auth_token.is_expired()

    def is_authenticated(self) -> bool:
        return not self.is_expired()
