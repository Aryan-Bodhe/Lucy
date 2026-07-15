from dataclasses import dataclass
from openai import (
    NotFoundError, 
    RateLimitError, 
    APIConnectionError, 
    AuthenticationError,
    OAuthError,
    OpenAIError
)

from lucy.agent.agent import run_agent
from lucy.context import token_manager
from lucy.logger import get_logger
from lucy.ui.renderer import ui
from lucy.config import CLEAR_TERMINAL_UPON_EXIT

logger = get_logger()

@dataclass
class AgentResponse:
    content: str
    usage: dict
    time: float


def handle_request(prompt: str) -> AgentResponse:
    try:
        with token_manager():
            response, time_elapsed = run_agent(prompt)
            return AgentResponse(
                response["content"][-1].get("text"), 
                response["metadata"]["usage"], 
                time_elapsed
            )
    except NotFoundError:
        ui.render_error("Selected model is not available. Please check model ID and try again.")
    except RateLimitError:
        ui.render_error("You have exhausted your token credits for selected model. Please check your API balance and try again.")
    except APIConnectionError:
        ui.render_error("Unable to connect to servers. Please check your internet connection and try again.")
    except (AuthenticationError, OAuthError, OpenAIError, ValueError):
        ui.render_error("Your API key is missing or invalid. Please run 'lucy login' in your terminal to set one.")
    except Exception as e:
        ui.render_error("An unexpected error occurred. Please restart the app and try again.")
        logger.exception(f"Unhandled exception")


def run_app():
    logger.info("Initialized Strands Coder Agent")
    ui.initialise()
    ui.render_banner()

    while True:
        with ui.render_request_lifecycle() as session:
            try:
                prompt = session.input()
            except KeyboardInterrupt:
                ui.terminate(CLEAR_TERMINAL_UPON_EXIT)
                raise

            response = handle_request(prompt)
            if response is not None:
                session.usage = response.usage
                session.time_elapsed = response.time
                session.print()
                ui.render_response(response.content)