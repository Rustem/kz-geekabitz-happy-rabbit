import binascii
import datetime
import json
import os

from django.conf import settings
from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone

from happyrabbit.abc.activity import Activity, Category
from happyrabbit.abc.json.encoders import SimpleJSONDecoder, SimpleJSONEncoder
from happyrabbit.abc.service.activity import Pagination, SearchQuery


class CategoryModel(Category, models.Model):
    category_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=16)
    description = models.CharField(max_length=1024, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # nullable to allow generic activities

    class Meta:
        db_table = "activity_category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class ActivityModel(Activity, models.Model):

    class Meta:
        db_table = "activity"
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    activity_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=16)
    description = models.CharField(max_length=1024, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # nullable to allow generic activities
    category = models.ForeignKey(CategoryModel, on_delete=models.SET_NULL, null=True)

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


DEFAULT_ACTIVITY_PAGE_SIZE = getattr(settings, 'ACTIVITY_PAGE_SIZE', 100)
DEFAULT_ACTIVITY_PAGINATION_TTL_MINUTES = getattr(settings, 'ACTIVITY_PAGINATION_TTL_MINUTES', 10)

class SearchQueryJSONEncoder(SimpleJSONEncoder):
    type = SearchQuery


class SearchQueryJSONDecoder(SimpleJSONDecoder):
    type = SearchQuery


class ActivityPaginationModel(Pagination, models.Model):

    pagination_token = models.CharField(max_length=21, primary_key=True)
    min_index = models.PositiveIntegerField()
    max_index = models.PositiveIntegerField()
    query = models.JSONField(encoder=SearchQueryJSONEncoder, decoder=SearchQueryJSONDecoder)
    created_at = models.DateTimeField(default=timezone.now)
    expire_at = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = "activity_pagination"
        verbose_name = "Pagination"
        verbose_name_plural = "Pagination Set"

    def save(self, **kwargs):
        if not self.expire_at:
            self.expire_at = self.created_at + datetime.timedelta(minutes=DEFAULT_ACTIVITY_PAGINATION_TTL_MINUTES)
        return super().save(**kwargs)

    def get_pagination_token(self) -> str:
        return self.pagination_token

    def get_min_index(self) -> int:
        return self.min_index

    def get_max_index(self) -> int:
        return self.max_index

    def get_query(self) -> SearchQuery:
        return self.query

    def get_page_size(self) -> int:
        return DEFAULT_ACTIVITY_PAGE_SIZE

    def get_created_at(self) -> datetime.datetime:
        return self.created_at

    def get_expire_at(self) -> datetime.datetime:
        return self.expire_at

    def get_owner_id(self) -> int:
        return self.owner.pk

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(21)).decode()


class RewardRule(models.Model):
    reward_rule_id = models.BigAutoField(primary_key=True)
    duration = models.PositiveIntegerField(help_text="Minimum duration in minutes", null=True)
    reward_carrots = models.IntegerField()
    activity = models.ForeignKey(ActivityModel, related_name='reward_rules', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Reward Rule"
        verbose_name_plural = "Reward Rules"
