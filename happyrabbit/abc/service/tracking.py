import uuid
from abc import abstractmethod, ABC
from typing import List

from happyrabbit.abc.activity import Category, Activity
from happyrabbit.abc.family import Child
from happyrabbit.abc.tracking import ActivityEvent


class ActivityTrackingService(ABC):

    @abstractmethod
    def add_event(self, child: Child, activity: Activity, category: Category = None, carrots: int = 0, duration: int = None) -> ActivityEvent:
        raise NotImplementedError("implement me")

    @abstractmethod
    def delete_event(self, event_id: uuid.UUID):
        raise NotImplementedError("implement me")

    @abstractmethod
    def delete_multiple_events(self, event_ids: List[uuid.UUID]) -> int:
        """
        @params {List[uuid.UUID]} event ids to delete
        @returns number of deleted objects
        """
        raise NotImplementedError("implement me")