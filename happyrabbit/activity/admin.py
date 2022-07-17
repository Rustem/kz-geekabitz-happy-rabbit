from django.contrib import admin

# Register your models here.
from happyrabbit.activity.models import Category, Activity, RewardRule

admin.site.register(Category)
admin.site.register(Activity)
admin.site.register(RewardRule)