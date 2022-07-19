from django.forms import ModelForm

from happyrabbit.activity.models import Category, ActivityModel, RewardRule


class CategoryCreateForm(ModelForm):
    class Meta:
        model = Category
        fields = ('title', 'description', )
        verbose_name_plural = "categories"


class ActivityCreateForm(ModelForm):
    class Meta:
        model = ActivityModel
        fields = ('title', 'description', 'category', )
        verbose_name_plural = "activities"


class RewardRuleCreateForm(ModelForm):
    class Meta:
        model = RewardRule
        fields = ('duration', 'reward_carrots', 'activity', )
        verbose_name_plural = "reward rules"
