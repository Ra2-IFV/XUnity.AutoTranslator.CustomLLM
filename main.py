import asyncio
import uvicorn

from config import load_config
from log import logger
from server import app

async def main() -> None:
    config = load_config()
    if config is not None:
        if config.server is not None:
            if config.server.port is not None:
                server_config = uvicorn.Config(app, port=config.server.port, log_level="info")
                server = uvicorn.Server(server_config)
                await server.serve()

    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Caught SIGINT')