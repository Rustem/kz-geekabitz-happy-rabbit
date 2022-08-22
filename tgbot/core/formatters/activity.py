from typing import List

from happyrabbit.abc.activity import Activity
from happyrabbit.activity.models import CONFIGURED_ACTIVITY_PAGE_SIZE


def inline_activity_list(page_number, activities: List[Activity]) -> str:
    """
    @returns formatted list of activities
    e.g.
    1. math
    2. science
    """
    page_size = CONFIGURED_ACTIVITY_PAGE_SIZE
    count_from = (page_number - 1) * page_size
    return '\n'.join(map(lambda x: f'{count_from + x[0] + 1}. {x[1].get_title().capitalize()}', enumerate(activities)))

