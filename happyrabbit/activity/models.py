from django.db import models

from django.contrib.auth.models import User

from happyrabbit.abc.activity import Activity


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


class ActivityModel(Activity, models.Model):

    class Meta:
        db_table = "hr_user_category"
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    activity_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=16)
    description = models.CharField(max_length=1024, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # nullable to allow generic activities
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    def get_activity_id(self) -> int:
        return self.activity_id

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_category_name(self):
        if not self.category:
            return None
        return self.category.title


class RewardRule(models.Model):
    reward_rule_id = models.BigAutoField(primary_key=True)
    duration = models.PositiveIntegerField(help_text="Minimum duration in minutes", null=True)
    reward_carrots = models.IntegerField()
    activity = models.ForeignKey(ActivityModel, related_name='reward_rules', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Reward Rule"
        verbose_name_plural = "Reward Rules"
