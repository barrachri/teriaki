import pytest

from aiohttp import web

from app import add_route


@pytest.fixture
def cli(loop, test_client):
    app = web.Application()
    add_route(app)
    return loop.run_until_complete(test_client(app))


async def test_get_index(cli):
    resp = await cli.get('/')
    assert resp.status == 200
    message = await resp.json()
    assert "message" in message


async def test_get_upload(cli):
    resp = await cli.get('/upload')
    assert resp.status == 200
    message = await resp.text()
    assert message
