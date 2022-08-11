import uuid
from typing import List

from happyrabbit.abc.activity import Activity, Category
from happyrabbit.abc.family import Child

from happyrabbit.abc.service.tracking import ActivityTrackingService
from happyrabbit.abc.tracking import ActivityEvent
from happyrabbit.tracking.models import ActivityEventModel


class DefaultActivityTrackingService(ActivityTrackingService):
    def add_event(self, child: Child, activity: Activity, category: Category = None, carrots: int = 0,
                  duration: int = None) -> ActivityEvent:
        activity_event = ActivityEventModel(child=child)
        activity_event.activity = activity
        activity_event.category = category
        activity_event.carrots = carrots
        activity_event.duration = duration
        activity_event.save()
        return activity_event

    def delete_event(self, event_id: uuid.UUID):
        ActivityEventModel.objects.filter(event_id=event_id).delete()

    def delete_multiple_events(self, event_ids: List[uuid.UUID]) -> List[uuid.UUID]:
        deleted_rows, _ = ActivityEventModel.objects.filter(event_id__in=event_ids).delete()
        return deleted_rows
