from abc import abstractmethod


class Category:

    def get_category_id(self) -> int:
        pass

    def get_title(self) -> str:
        pass

    def get_description(self) -> str:
        pass


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