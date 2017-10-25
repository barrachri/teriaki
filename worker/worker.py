"""
Views for Teriaki app.

worker.py

"""


import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
import os
import time
import smtplib
from email.message import EmailMessage

import msgpack
import aio_pika
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
CSV_FOLDER = os.path.join(BASE_DIR, "csv_folder")
SMTP_SERVER = ""  # SMTP server
SMTP_PORT = 0  # SMTP port
EMAIL_USER = ""  # SMTP user
EMAIL_PASSWORD = ""  # SMTP password
EMAIL_SENDER = ""  # Email receiver

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.basicConfig(format=FORMAT)


def processing_csv(filename: str):
    """
    Receive a filename available in the local path and process it.

    :filename: path available locally

    """
    log.info(f"Processing file {filename}")

    now = time.time()

    csv_file = os.path.join(CSV_FOLDER, filename)

    try:
        df = pd.read_csv(csv_file)
        describe = df.describe()
        os.remove(csv_file)

    except Exception:
        log.exception("Error while processing the csv file.")
        describe = None

    finally:
        total_time = time.time() - now

    return describe, total_time


def send_email(email: str, df: pd.DataFrame):
    """
    Send an email.

    :to: recevier of the email
    :from: sender
    :subject: subject of the email
    :df: Dataframe object
    """
    msg = EmailMessage()

    msg['Subject'] = 'Greetings from Teriaki'
    msg['From'] = "barrachri@gmail.com"
    msg['To'] = email

    if df is None:
        log.error("Empty dataframe")
    else:
        msg.set_content(df.to_html(), subtype='html')

    # Send the email via our own SMTP server.
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as s:
        s.login(EMAIL_USER, EMAIL_PASSWORD)
        s.send_message(msg)


async def subscriber(loop, executor):
    """
    Subscribe to a rabbitmq topic and execute some tasks depending from the event.

    :loop: event loop
    :executor: executor pool
    """
    connection = await aio_pika.connect_robust("amqp://guest:guest@0.0.0.0/", loop=loop)
    queue_name = "test_queue"
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name, auto_delete=True)

    log.info("Event connected")

    async for message in queue:
        log.info("Event received")
        with message.process():

            event = msgpack.unpackb(message.body, encoding='utf-8')

            email = event["email"]
            filename = event["filename"]

            # convert the csv
            output, total_time = processing_csv(filename)
            log.info(f"Processing total time {total_time}")

            log.info('Executing blocking task')
            blocking_task = loop.run_in_executor(executor, send_email, email, output)
            await blocking_task


if __name__ == "__main__":
    # Create a limited process pool with 2 workers
    executor = ProcessPoolExecutor(max_workers=2)
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(subscriber(loop, executor))
    finally:
        loop.close()
