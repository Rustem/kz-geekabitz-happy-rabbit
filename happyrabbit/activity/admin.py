from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin

from happyrabbit.activity.models import Category, Activity, RewardRule


class CategoryAdmin(ModelAdmin):
    list_display = ['category_id', 'title', 'description']
    ordering = ['category_id']


class ActivityAdmin(ModelAdmin):
    list_display = ['activity_id', 'title', 'description', 'category']
    ordering = ['activity_id']


class RewardRuleAdmin(ModelAdmin):
    list_display = ['reward_rule_id', 'duration', 'reward_carrots', 'activity']
    ordering = ['reward_rule_id']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(RewardRule, RewardRuleAdmin)
