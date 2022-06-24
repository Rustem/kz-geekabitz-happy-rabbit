from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    account_id = models.IntegerField(primary_key=True)
    external_service = models.CharField(max_length=200)
    external_user_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class UserProfile(models.Model):
    user_profile_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    language_code = models.CharField(max_length=2, blank=True)
    username = models.CharField(max_length=200, null=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class Child(models.Model):
    child_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    carrots = models.IntegerField(default=0)
    guardian_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if self.age > 18:
            raise ValidationError("Child must be younger than 18!")