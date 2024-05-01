"""The main driver for beginning the program's execution"""

import asyncio

from api import app
from hypercorn.asyncio import serve
from hypercorn.config import Config

if __name__ == "__main__":
    config = Config()
    config.bind = ["10.0.0.4:5000"]

    asyncio.run(serve(app, config))
