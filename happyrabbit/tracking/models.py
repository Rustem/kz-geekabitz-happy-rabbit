import uuid
import datetime
from django.db import models
from django.utils import timezone
from happyrabbit.abc.activity import Category, Activity
from happyrabbit.abc.json.encoders import DjangoModelJSONEncoder, DjangoModelJSONDecoder
from happyrabbit.abc.tracking import ActivityEvent
from happyrabbit.abc.family import Child


class ActivityEventModel(ActivityEvent, models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey('hr_user.ChildModel', on_delete=models.CASCADE)
    category = models.JSONField(null=True, encoder=DjangoModelJSONEncoder, decoder=DjangoModelJSONDecoder)
    activity = models.JSONField(encoder=DjangoModelJSONEncoder, decoder=DjangoModelJSONDecoder)
    duration = models.PositiveIntegerField(help_text="Duration in minutes", null=True)
    carrots = models.PositiveIntegerField(help_text="Earned carrots")
    time_created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "tracking_activity_event"
        verbose_name = "Activity Event"
        verbose_name_plural = "Activity Events"

    def get_event_id(self) -> uuid.UUID:
        return self.event_id

    def get_child(self) -> Child:
        return self.child

    def get_activity(self) -> Activity:
        return self.activity

    def get_category(self) -> Category:
        return self.category

    def get_duration(self) -> int:
        """Duration in minutes"""
        return self.duration

    def get_carrots(self) -> int:
        return self.carrots

    def get_time_created(self) -> datetime.datetime:
        return self.time_created
