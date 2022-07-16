from abc import abstractmethod


class Child:

    @abstractmethod
    def get_child_id(self) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_age(self) -> int:
        pass

    @abstractmethod
    def get_carrots(self) -> int:
        pass

    @abstractmethod
    def get_guardian(self):
        pass


class BaseChildren:

    @abstractmethod
    def get_child(self, child_idx: int) -> Child:
        pass

    @abstractmethod
    def get_child_by_name(self, name: str) -> Child | None:
        pass

    @property
    @abstractmethod
    def family_size(self) -> int:
        pass

    def __iter__(self):
        return self

    def __next__(self) -> Child:  # Python 2: def next(self)
        raise NotImplementedError("implement iterator")

