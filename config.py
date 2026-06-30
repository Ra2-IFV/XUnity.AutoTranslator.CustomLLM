import tomllib
from typing import Any
from pathlib import Path
from pydantic import BaseModel, ValidationError

class ServerConfig(BaseModel):
    host: str | None = '0.0.0.0'
    port: int | None = 18081

class LLMConfig(BaseModel):
    api_key: str
    model: str
    url: str

class PromptConfig(BaseModel):
    use_base: bool = True
    user: str = ''
    system: str = ''

class FullConfig(BaseModel):
    name: str
    server: ServerConfig
    llm: LLMConfig
    prompt: PromptConfig
    extra_body: dict[str, Any] | None = None
    extra_headers: dict[str, Any] | None = None

def load_config() -> FullConfig | None:
    path: Path = Path().cwd() / 'config.toml'

    try:
        with open(path, 'rb') as f:
            data: dict[str, Any] = tomllib.load(f)
            return FullConfig(**data)

    except:
        raise