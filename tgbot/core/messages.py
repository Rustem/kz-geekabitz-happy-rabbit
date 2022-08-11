AUTH_ALREADY = """
This chat is already authorized. 
To get more details, use /status.
"""


COMMAND_NOT_FOUND = """
Command {command} does not exist. 
Try /help for list of available commands.
"""

LOGIN_REQUIRED = """
You need to be *authenticated* to perform this action.
Please login following the link below. 
*Link*: {login_url}.
"""

INVALID_AUTH_KEY = """
There is no active authentication key associated with this account. 
Please login following the link below.
*Link*: {login_url}
"""

WELCOME_AUTHENTICATED_USER = """
Welcome back, @{username}. Hope {children} are doing well.
"""

WELCOME_NOT_AUTHENTICATED_USER = """
HI, {username}. Looks like your session is expired. 
Please login following the link below.
*Link*: {login_url}
"""

HELP = """
Available commands:

{available_commands}
"""

#
# /status
#

STATUS_INVALID_TOKEN = """
This account is not authenticated.
Use /start to login in Happy Rabbit.
"""

STATUS_OK = """
You are authenticated as @{username} at {date_logged_in}. 
Try /help for list of available commands.
"""

#
# /show_activities {category}
#
SHOW_ACTIVITIES_MISS_CATEGORY = """
You have too many activities. Please include category in the request.
Example: /show\\_activities science 
"""

SHOW_ACTIVITIES_OK = """
Here is your activities:
{inline_activities}
"""