import os
import time
import keyring

from strands import Agent, ModelRetryStrategy
from strands.models.openai import OpenAIModel
from strands.vended_plugins.skills import AgentSkills

from lucy.agent.hooks import ProgressHook
from lucy.agent.tools import ALL_TOOLS
from lucy.agent.interventions import SensitiveToolApproval
from lucy.agent.prompts.system_prompt import PROMPT
from lucy.agent.utils import get_prompt_metadata

from lucy.ui.renderer import ui

from lucy.logger import get_logger
from lucy.config import MODEL, SKILLS_DIR, APP_NAME, MODEL_PROVIDER

logger = get_logger()

_agent = None
_tools = ALL_TOOLS
_skills = AgentSkills(skills=SKILLS_DIR)

def _init_model():
    _api_key = keyring.get_password(APP_NAME, MODEL_PROVIDER)
    if not _api_key:
        logger.error("OpenAI API key not set.")
        raise ValueError("OpenAI API key not set.")
    return OpenAIModel(
        model_id=MODEL,
        client_args={
            "api_key": _api_key
        }
    )

def _get_or_create_agent():
    global _agent
    if _agent:
        return _agent
    logger.info("Initializing Strands Agent.")
    _model = _init_model()
    logger.info("OpenAI model instance created successfully.")

    _agent = Agent(
        model=_model, 
        system_prompt=PROMPT,
        tools=_tools,
        plugins=[_skills],
        hooks=[ProgressHook()],
        interventions=[SensitiveToolApproval()],
        callback_handler=None,
        retry_strategy=ModelRetryStrategy(
            max_attempts=3
        )
    )

    logger.info("Created Agent instance successfully.")
    return _agent


def run_agent(prompt: str):
    logger.info(f"Running agent with prompt: {prompt}")
    agent = _get_or_create_agent() 
    prompt = prompt + get_prompt_metadata()

    start = time.perf_counter()
    response = agent(prompt)
    end = time.perf_counter()

    elapsed = round(end-start, 2)
    usage = response.metrics.accumulated_usage
    
    logger.info(
        "token_usage=%d/%d/%d/%d resp_time=%.2fs",
        usage["inputTokens"],
        usage["outputTokens"],
        getattr(usage, "cacheReadInputTokens", 0),
        getattr(usage, "cacheWriteInputTokens", 0),
        elapsed,
    )
    return response.message, elapsed
