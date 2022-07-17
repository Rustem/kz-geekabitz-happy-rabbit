from happyrabbit.abc.family import BaseChildren
from happyrabbit.abc.service.family import BaseFamilyService
from happyrabbit.hr_user.models import ChildModel, Children


class FamilyService(BaseFamilyService):

    def get_children(self, guardian_id: int) -> BaseChildren:
        children_list = ChildModel.objects.filter(guardian__pk=guardian_id).all()
        return Children(children_list)
