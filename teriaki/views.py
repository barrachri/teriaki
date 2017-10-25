"""
Views for Teriaki app.

views.py

"""


import os
import logging
from uuid import uuid4

from aiohttp.web import json_response
from aiohttp.web import Response
import aio_pika
import msgpack


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FOLDER = os.path.join(BASE_DIR, "csv_folder")


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)


page = '''
<form action="/upload" method="post" accept-charset="utf-8"
      enctype="multipart/form-data">

    <label for="email">Email</label>
    <input id="email" name="email" type="email" value=""/>

    <label for="csv">csv</label>
    <input id="csv" name="csv" type="file" value=""/>

    <input type="submit" value="submit"/>
</form>
'''


async def welcome(request):
    """Just a simple welcome api."""
    return json_response({'message': 'Welcome to Teriaki!'})


async def save_multipart(request):
    """Handle a multipart form."""
    multipart = await request.multipart()
    out = {}
    while True:
        field = await multipart.next()
        if not field:
            break
        size = 0
        content_type = field.headers.get('CONTENT-TYPE')

        if field.filename:
            _, extension = os.path.splitext(field.filename)
            csv_filename = "".join((uuid4().hex, ".csv"))
            out["csv_filename"] = csv_filename

            if extension != ".csv":
                return json_response({'message': f'We only process csv files'})

            with open(os.path.join(CSV_FOLDER, csv_filename), 'wb') as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)
        else:
            value = await field.read(decode=True)
            if content_type is None or \
                    content_type.startswith('text/'):
                charset = field.get_charset(default='utf-8')
                value = value.decode(charset)
            out[field.name] = value
            size += len(value)

    return out


async def upload(request):
    """Upload the file a save it with a local uuid."""
    if request.method == 'POST':

        log.debug("Received POST request")

        data = await save_multipart(request)
        if 'email' in data:
            email = data['email']
        if 'csv_filename' in data:
            csv_filename = data['csv_filename']

        log.info("Hello")

        connection = await aio_pika.connect_robust("amqp://guest:guest@0.0.0.0/")

        async with connection:
            routing_key = "test_queue"

            channel = await connection.channel()

            event = msgpack.packb({"filename": csv_filename, "email": email})

            await channel.default_exchange.publish(
                aio_pika.Message(body=event),
                routing_key=routing_key
                )

        return json_response({'message': f'Your file will be processed soon.'})

    log.debug("Received GET request")

    return Response(body=page, content_type="text/html")
