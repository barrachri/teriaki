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

    <label for="csv">csv</label>
    <input id="csv" name="csv" type="file" value=""/>

    <input type="submit" value="submit"/>
</form>
'''


async def welcome(request):
    """Just a simple welcome api."""
    return json_response({'message': 'Welcome to Teriaki!'})


async def upload(request):
    """Upload the file a save it with a local uuid."""
    if request.method == 'POST':

        log.debug("Received POST request")

        reader = await request.multipart()
        email = "barrachri@gmail.com"

        _csv = await reader.next()

        _, extension = os.path.splitext(_csv.filename)

        if extension != ".csv":
            return json_response({'message': f'We only process csv files'})

        uuid_name = uuid4().hex
        csv_filename = "".join((uuid_name, ".csv"))

        size = 0
        with open(os.path.join(CSV_FOLDER, csv_filename), 'wb') as f:
            while True:
                chunk = await _csv.read_chunk()
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)

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
