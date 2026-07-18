import keyring
from strands import Agent
from strands.models.openai import OpenAIModel
from openai import AuthenticationError

from lucy.config import APP_NAME, MODEL, SUPPORTED_PROVIDERS
from lucy.logger import get_logger

logger = get_logger()


def get_api_key(provider: str):
    return keyring.get_password(APP_NAME, provider)


def validate_api_key(api_key: str, provider: str, model_id: str):
    model = OpenAIModel(
        model_id=model_id,
        client_args={"api_key": api_key}
    )
    agent = Agent(model=model, callback_handler=None)
    try: 
        _ = agent("Say OK.")
        logger.info(f"API key validated for provider={provider}")
        return True
    except AuthenticationError:
        logger.warning(f"Incorrect API key received for provider={provider}")
        return False
    except Exception:
        raise


def store_api_key(api_key: str, provider: str = MODEL):
    if validate_api_key(api_key, provider, model_id=MODEL):
        keyring.set_password(APP_NAME, provider, api_key)
        logger.info(f"API key stored in keyring for provider={provider}")
        return True
    return False


def delete_api_key(provider: str):
    if get_api_key(provider) is None:
        return False
    logger.info(f"API Key deleted for provider={provider}")
    keyring.delete_password(APP_NAME, provider)
    return True