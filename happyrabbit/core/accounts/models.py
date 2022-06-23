from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    external_service = models.CharField(max_length=200)
    external_user_id = models.IntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class UserProfile(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    language_code = models.CharField(max_length=2)
    username = models.CharField(max_length=200)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class Child(models.Model):
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    carrots = models.IntegerField()
    guardian_id = models.ForeignKey(User, on_delete=models.CASCADE)
