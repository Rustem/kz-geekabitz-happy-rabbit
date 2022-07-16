from abc import abstractmethod, ABC
from typing import List

from happyrabbit.abc.family import BaseChildren


class BaseFamilyService(ABC):

    @abstractmethod
    def get_children(self, guardian_id: int) -> BaseChildren:
        f"""
        @param {int} guardian_id - user id of a parent
        @returns {BaseChildren} children of the parent
        """
        raise NotImplementedError("not implemented")