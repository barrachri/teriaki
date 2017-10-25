"""
Launcher for teriaki app.

app.py

"""

import asyncio
from concurrent.futures import ProcessPoolExecutor

from aiohttp import web
from teriaki.routes import routes
from worker import subscriber


def add_route(app):
    """
    Add routes to app instance.

    :app: instance of the app
    """
    for route in routes:
        app.router.add_route(route[0], route[1], route[2])


async def start_background_tasks(app):
    """Load a background task executor."""
    executor = ProcessPoolExecutor(max_workers=2)
    app.loop.create_task(subscriber(app.loop, executor))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    add_route(app)
    app.on_startup.append(start_background_tasks)
    web.run_app(app, host='127.0.0.1', port=8080)
