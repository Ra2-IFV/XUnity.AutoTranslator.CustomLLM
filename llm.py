from typing import Any
from string import Template
from openai import AsyncOpenAI, APIStatusError

from config import load_config, FullConfig
from log import logger
from utils.file import read_file_to_str

config: FullConfig | None = load_config()
if config is None:
    raise ValueError

client = AsyncOpenAI(
    api_key = config.llm.api_key,
    base_url = config.llm.url
)

lang: dict[str, str] = {
    'en': 'English',
    'ja': 'Japanese',
    'zh-CN': 'Simplified Chinese'
}

def build_user_prompt(from_lang: str, to_lang: str, text: str) -> str:
    user_prompt: str = config.prompt.user

    if config.prompt.use_base:
        base: str = read_file_to_str(path='prompts/base_user.txt')

        try:
            base_templated = Template(base).substitute(
                game_name = config.name,
                from_language = lang[from_lang],
                to_language = lang[to_lang],
                text = text
            )
        except ValueError:
            logger.error('Failed to template base prompt')
            raise

        final_prompt = base_templated + user_prompt
    else:
        final_prompt = user_prompt

    return final_prompt

def build_message(user_prompt: str) -> list[dict[str, str]]:
    system_prompt: str = config.prompt.system
    messages: list[dict[str, str]] = [{ 'role': 'user', 'content': user_prompt }]

    if system_prompt != '':
        messages.append({ 'role': 'system', 'content': system_prompt })

    return messages

async def get_completion_api(messages: list[Any]) -> str | None:
    completion = None

    try:
        completion = await client.chat.completions.create(
            model=config.llm.model,
            messages=messages,
            extra_body=config.extra_body,
            extra_headers=config.extra_headers
        )

    except APIStatusError as e:
        match e.status_code:
            case 400:
                logger.warning(f'Request failed: Bad request: {e.body}')
            case 429:
                logger.warning(f'Request failed: Limit exceeded: {e.body}')
            case _:
                logger.error(f'Request failed: {e.status_code} {e.body}')
        return None

    except Exception:
        logger.exception(Exception)
        return None

    return completion.choices[0].message.content

async def get_response_api(model_input: str | list[Any]) -> str | None:
    response = None
    
    try:
        response = await client.responses.create(
            model=config.llm.model,
            input=model_input
        )
    
    except APIStatusError as e:
        match e.status_code:
            case 400:
                logger.warning(f'Request failed: Bad request: {e.body}')
            case 429:
                logger.warning(f'Request failed: Limit exceeded: {e.body}')
            case _:
                logger.error(f'Request failed: {e.status_code} {e.body}')
        return None
    
    except Exception:
        logger.exception(Exception)
        return None

    return response.output_text