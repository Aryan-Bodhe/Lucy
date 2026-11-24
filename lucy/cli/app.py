from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any
from openai import (
    NotFoundError, 
    RateLimitError, 
    APIConnectionError, 
    AuthenticationError,
    OAuthError,
    OpenAIError
)
from strands.agent import AgentResult

from lucy.agent.agent import run_agent, generate_title, clean_title
from lucy.logger import get_logger
from lucy.ui.core import ui
from lucy.cli.utils import compute_usage_metrics
from lucy.config import CLEAR_TERMINAL_UPON_EXIT, MODEL
from lucy.session.manager import SessionManager
from lucy.session.models import UsageMetrics

logger = get_logger(__name__)


@dataclass
class AgentResponse:
    content: str
    usage: UsageMetrics  # this turn only; session totals live in session metadata
    time: float



def _handle_request(prompt: str) -> AgentResponse | None:
    """Run one agent turn. Returns None after rendering an error."""
    try:
        response, time_elapsed = run_agent(prompt)
        answer = response.message["content"][-1].get("text")
        return AgentResponse(
            answer,
            compute_usage_metrics(response),
            time_elapsed
        )
    except NotFoundError:
        ui.responses.render_error("Selected model is not available. Please check model ID and try again.")
    except RateLimitError:
        ui.responses.render_error("You have exhausted your token credits for selected model. Please check your API balance and try again.")
    except APIConnectionError:
        ui.responses.render_error("Unable to connect to servers. Please check your internet connection and try again.")
    except (AuthenticationError, OAuthError, OpenAIError, ValueError):
        ui.responses.render_error("Your API key is missing or invalid. Please run 'lucy login' in your terminal to set one.")
    except Exception as e:
        ui.responses.render_error("An unexpected error occurred. Please restart the app and try again.")
        logger.exception(f"Unhandled exception")



def handle_request(session_manager: SessionManager):

    try:
        prompt = ui.input()
    except KeyboardInterrupt:
        ui.terminate(CLEAR_TERMINAL_UPON_EXIT)
        logger.info("Terminating session")
        raise

    session_manager.append_transcript(
        role="user",
        message=prompt
    )
    ui.print()
    logger.info("User prompt transcribed")

    if prompt.strip() and not session_manager.is_session_titled():
        title = generate_title(prompt) or clean_title(prompt)
        if title:
            session_manager.set_session_title(title)

    with session_manager.request_scope():
        response = _handle_request(prompt)

        if response is None:
            # The error has already been rendered; keep the session alive.
            logger.warning("Agent request failed; no response to record")
            return

        session_manager.append_transcript(
            role="agent",
            message=response.content
        )
        logger.info("Agent response transcribed")

        session_manager.update_metadata(
            model_id=MODEL,
            usage=response.usage
        )

        logger.info("Metadata updated")

        rule_title = ""
        try:
            cu = response.usage
            rule_title = f"Input={cu.input_tokens} Output={cu.output_tokens} Time={response.time}s Context_used={cu.context_used_pct}% Cost=${cu.cost_usd}"
        except Exception:
            logger.exception("Failed to print metrics")

        ui.responses.render_response(response.content)
        ui.print()
        ui.rule(rule_title)



def run_app():
    logger.info("Initialized Strands Coder Agent")
    session_manager = SessionManager()
    with session_manager.session_scope():
        logger.info("New session initialised")
        ui.initialise()
        ui.banner.render()

        while True:
            handle_request(session_manager)