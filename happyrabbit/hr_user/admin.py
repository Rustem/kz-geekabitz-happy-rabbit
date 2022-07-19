import nested_admin.nested
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Account, UserProfile, ChildModel


class ChildInline(nested_admin.nested.NestedStackedInline):
    model = ChildModel
    extra = 1
    exclude = ['child_id']


class UserProfileInline(nested_admin.nested.NestedStackedInline):
    model = UserProfile
    extra = 1
    exclude = ['user_profile_id']


class AccountInline(nested_admin.nested.NestedStackedInline):
    model = Account
    extra = 1
    inlines = [UserProfileInline]
    exclude = ['account_id']


class CustomUserAdmin(nested_admin.nested.NestedModelAdmin, UserAdmin):
    inlines = [AccountInline, ChildInline]
    list_display = ['email', 'username', 'is_staff', 'is_active', 'get_children']

    def get_children(self, obj):
        children = obj.child_set.all()
        return '\n'.join(map(str, children))

    get_children.short_description = "Children"


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

