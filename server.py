from llm import get_completion_api
from typing import Any, Awaitable, Callable, Dict
from urllib.parse import parse_qs

from log import logger
from llm import build_user_prompt, build_message, get_completion_api

Scope = Dict[str, Any]
Receive = Callable[[], Awaitable[Dict[str, Any]]]
Send = Callable[[Dict[str, Any]], Awaitable[None]]


def _parse_query_string(raw_qs: bytes) -> dict[str, list[str]] | None:
    try:
        return parse_qs(qs=raw_qs.decode(), strict_parsing=True)

    except ValueError:
        logger.warning('ValueError in parsing query string')
        logger.warning(raw_qs)
        return None

def _get_query_string_value(qs: dict[str, list[str]], keys: list[str]) -> list[str | None]:
    """
    [0]: from
    [1]: to
    [2]: text to translate
    """
    values: list[str | None] = []

    for k in keys:
        if k in qs:
            for v in qs[k]:
                values.append(v)
        else:
            logger.warning('Missing query string key: ' + k)
            values.append(None)

    return values

async def send_simple_response(status: int, body: str, send: Send) -> None:
    """
    status: HTTP status code
    body: HTTP body in string
    """
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [(b"content-type", b"text/plain; charset=UTF-8")],
        }
    )
    await send({"type": "http.response.body", "body": bytes(body, "utf-8")})


async def app(scope: Scope, receive: Receive, send: Send) -> None:
    if scope["type"] != "http":
        return

    if scope["method"] != "GET":
        return await send_simple_response(405, 'Method Not Allowed', send)

    if scope["path"] != "/translate":
        return await send_simple_response(200, 'OK', send)

    raw_qs: bytes = scope["query_string"]

    qs: dict[str, list[str]] | None = _parse_query_string(raw_qs)
    if qs is None:
        return await send_simple_response(400, 'Bad Request', send)

    qs_values: list[str | None] = _get_query_string_value(qs, ['from', 'to', 'text'])
    if None in qs_values:
        return await send_simple_response(400, 'Bad Request', send)

    user_prompt: str = build_user_prompt(
        # pyrefly: ignore [bad-argument-type]
        from_lang=qs_values[0],
        # pyrefly: ignore [bad-argument-type]
        to_lang=qs_values[1],
        # pyrefly: ignore [bad-argument-type]
        text=qs_values[2]
    )
    
    messages: list[dict[str, str]] = build_message(user_prompt)
    response_body: str | None = await get_completion_api(messages)

    if response_body is None:
        return await send_simple_response(500, 'WTF', send)
    else:
        return await send_simple_response(200, response_body, send)