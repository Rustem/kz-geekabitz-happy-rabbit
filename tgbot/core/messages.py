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
Please login following this link {login_url}
"""

INVALID_AUTH_KEY = """
Sorry, we cannot authenticate you. There is no active authentication key. 
Please login following this link {login_url}  
"""

WELCOME_AUTHENTICATED_USER = """
Welcome back {username}. 
"""

WELCOME_NOT_AUTHENTICATED_USER = """
HI, {username}. Looks like your session is expired. Please login following this link {login_url}
"""