import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from strands.agent import AgentResult

@dataclass
class TextEvent:
    text: str

@dataclass
class ToolStartEvent:
    tool: str
    args: dict

@dataclass
class ToolEndEvent:
    result: Any

@dataclass
class FinishedEvent:
    result: AgentResult
    usage: dict
    elapsed: float


def parse_tool_parameters(tool_name: str, tool_input: dict):
    message = ""
    if tool_name == "editor":
        cmd = tool_input.get("command") or ""
        path = tool_input.get("path") or ""
        view_range = tool_input.get("view_range") or ""

        message = f"{cmd} {path}"
        message += f" range={view_range}" if view_range else ""
        
        return message
    
    elif tool_name == "shell":
        message = tool_input.get("command")
        return message
    
    elif tool_name == "handoff_to_user":
        return None
    
    elif tool_name == "skills":
        skill_name = tool_input.get("skill_name")
        return skill_name
    
def has_sudo_access() -> bool:
    """
    Returns True if sudo credentials are already cached.
    Does not prompt the user.
    """
    result = subprocess.run(
        ["sudo", "-n", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0

def gain_sudo_privileges(password: str):
        """
        Ensures sudo authentication is available.

        Returns:
            True  -> sudo is ready
            False -> user cancelled or authentication failed

        get_password() should return:
            password (str)  -> user entered one
            None            -> user cancelled (Esc)
        """

        if password is None:
            return False

        proc = subprocess.run(
            ["sudo", "-S", "-p", "", "-v"],
            input=password + "\n",
            text=True,
            capture_output=True,
        )

        # Drop our reference immediately.
        del password
            
        return proc.returncode == 0

def get_prompt_metadata():
    return f"""
        Current repository root: {os.getcwd()}
        Current date: {datetime.today()}
        Current locale: {datetime.now().astimezone().tzinfo}
    """