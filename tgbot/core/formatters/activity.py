from typing import List

from happyrabbit.abc.activity import Activity


def inline_activity_list(activities: List[Activity]) -> str:
    """
    @returns formatted list of activities
    e.g.
    1. math
    2. science
    """
    return '\n'.join(map(lambda x: f'{x[0] + 1}. {x[1].get_title().capitalize()}', enumerate(activities)))

