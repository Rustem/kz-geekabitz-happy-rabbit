from abc import abstractmethod


class Activity:

    @abstractmethod
    def get_activity_id(self) -> int:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def get_category_name(self) -> str:
        pass