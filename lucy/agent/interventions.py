import subprocess
from strands.interventions import (
    InterventionHandler,
    Proceed,
    Confirm,
    Deny
)
from lucy.agent.tools import SENSITIVE_TOOLS
from lucy.agent.utils import parse_tool_parameters

from lucy.ui.core import ui

from lucy.logger import get_logger

logger = get_logger()

class SensitiveToolApproval(InterventionHandler):
    name = "sensitive-tool-approval"

    def before_tool_call(self, event, **kwargs):
        tool_name = event.tool_use["name"]
        if tool_name in SENSITIVE_TOOLS:
            command = parse_tool_parameters(tool_name, event.tool_use['input'])
            logger.info(f"Requested user approval for tool: [{tool_name}] {command}")
            response = ui.approvals.render_approval(tool_name, command)
            return Confirm(response=response)
        return Proceed()
    

class SudoPasswordHandler(InterventionHandler):
    name = "sudo-password-handler"

    def _has_sudo_access(self) -> bool:
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
    
    def _gain_sudo_privileges(self, password: str):
        """
        Ensures sudo authentication is available.

        Returns:
            True  -> sudo is ready
            False -> user cancelled or authentication failed

        get_password() should return:
            password (str)  -> user entered one
            None            -> user cancelled (Esc)
        """

        if self._has_sudo_access():
            return True

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

        if proc.returncode == 0:
            logger.info("Sudo authentication successful.")
            
        return proc.returncode == 0

    def after_tool_call(self, event, **kwargs):
        if not event.result.get("status") == "error":
            return Proceed()
        
        content = event.result.get("content")
        for lines in content:
            if "permission denied" in lines.get("text").lower():
                tool_name = event.tool_use["name"]
                command = parse_tool_parameters(tool_name, event.tool_use['input'])
                password = ui.approvals.render_sudo_permission_request(tool_name, command)
                
                if self._gain_sudo_privileges(password):
                    return Proceed("User has granted sudo permissions. Retry the earlier failed commands with sudo.")
                else: 
                    return Deny("User cancelled sudo authentication.")
                
        return Proceed()