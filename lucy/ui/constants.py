from lucy.config import AGENT_NAME

SDOT = "●"
HDOT = "○"
TICK = "✔"
CROSS = "✘"
CAUTION = "!"
MISSING = "?"

WELCOME_TEXT = f"Welcome to {AGENT_NAME}, your personal AI coding copilot!"

TOOL_TEXT = f"""
🔧  {AGENT_NAME} wants to invoke a tool.
""" + """
    Tool: {tool_name}
    Command: {tool_command}

    Press Enter/y/yes to approve, or Escape/n/no to deny.
"""

PLAN_APPROVAL_TEXT = f"""
    {AGENT_NAME} has produced a plan. Would you like to proceed? (y/*)
"""

SUDO_PERMISSION_REQUEST_TEXT = f"""
🔒  {AGENT_NAME} requires sudo permission to run the following command.
""" + """
    Tool: {tool_name}
    Command: {tool_command}

    Type sudo password and press Enter to approve, or press escape to refuse.
"""

SIGNOFF_TEXT = f"Agent {AGENT_NAME} signing off. See you next time! 👋"