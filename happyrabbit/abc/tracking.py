import datetime
import uuid
from abc import abstractmethod

from happyrabbit.abc.activity import Activity, Category
from happyrabbit.abc.family import Child


class ActivityEvent:

    @abstractmethod
    def get_event_id(self) -> uuid.UUID:
        pass

    @abstractmethod
    def get_child(self) -> Child:
        pass

    @abstractmethod
    def get_activity(self) -> Activity:
        pass

    @abstractmethod
    def get_category(self) -> Category:
        pass

    @abstractmethod
    def get_duration(self) -> int:
        """Duration in minutes"""
        pass

    @abstractmethod
    def get_carrots(self) -> int:
        pass

    @abstractmethod
    def get_time_created(self) -> datetime.datetime:
        pass
