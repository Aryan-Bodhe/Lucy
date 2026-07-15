from strands.hooks import (
    HookProvider,
    HookRegistry,
    BeforeToolCallEvent, 
    AfterToolCallEvent
)
from lucy.ui.renderer import ui
from lucy.agent.utils import parse_tool_parameters
from lucy.logger import get_logger

logger = get_logger()


class ProgressHook(HookProvider):
    def register_hooks(self, registry: HookRegistry, **kwargs):
        registry.add_callback(BeforeToolCallEvent, self.before_tool)
        registry.add_callback(AfterToolCallEvent, self.after_tool)
    
    def before_tool(self, event: BeforeToolCallEvent):
        tool_name = event.tool_use["name"]
        tool_input = event.tool_use["input"]
        tool_command = parse_tool_parameters(tool_name, tool_input)
        logger.info(
            "Calling tool=%s input=%s", 
            event.tool_use["name"], 
            event.tool_use["input"]
        )
        tool_type = "skill" if tool_name == "skills" else "tool"
        ui.render_tool_status(
            tool_name if tool_type == "tool" else tool_command,
            tool_command=tool_command,
            tool_type=tool_type,
            status="running"
        )

    def after_tool(self, event: AfterToolCallEvent):
        tool_name = event.tool_use["name"]
        tool_input = event.tool_use["input"]
        tool_command = parse_tool_parameters(tool_name, tool_input)
        tool_type = "skill" if tool_name == "skills" else "tool"

        status = "success"
        if event.exception:
            status = "failed"
            logger.error(
                "Tool failed: %s %s",
                tool_name,
                tool_command,
                exc_info=event.exception
            )
        elif event.result.get("status") == "error":
            status = "failed"
            logger.warning(
                "Tool failed: %s %s",
                tool_name,
                tool_command
            )
        elif event.cancel_message:
            status = "refused"
            logger.info(
                "User refused tool: %s %s",
                tool_name,
                tool_command
            )
        
        logger.info(
            "Tool succeeded: %s %s",
            tool_name,
            tool_command
        )
        ui.render_tool_status(
            tool_name if tool_type == "tool" else tool_command,
            tool_command=tool_command,
            tool_type=tool_type,
            status=status
        )