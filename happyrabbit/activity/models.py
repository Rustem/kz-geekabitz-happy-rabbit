from django.db import models

from django.contrib.auth.models import User


class Category(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=16)
    description = models.CharField(max_length=1024, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # nullable to allow generic activities

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class Activity(models.Model):
    activity_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=16)
    description = models.CharField(max_length=1024, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # nullable to allow generic activities
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    def __str__(self):
        return self.title


class RewardRule(models.Model):
    reward_rule_id = models.BigAutoField(primary_key=True)
    duration = models.PositiveIntegerField(help_text="Minimum duration in minutes", null=True)
    reward_carrots = models.IntegerField()
    activity = models.ForeignKey(Activity, related_name='reward_rules', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Reward Rule"
        verbose_name_plural = "Reward Rules"
