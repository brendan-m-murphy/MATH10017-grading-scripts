import asyncio # for local testing
from aiosmtpd.controller import Controller
from smtplib import SMTP as Client
from pathlib import Path
import smtplib
import configparser

from unittest import TestCase, main
from email_grades import make_email
from email_grades import smtp_server

class ExampleHandler:
    async def handle_RCPT(self, server, session, envelope, address, rctp_options):
        if not address.endswith('@bristol.ac.uk'):
            return '550 not relaying to the domain'
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        print(f"Message from {envelope.mail_from}")
        print(f"Message for {envelope.rcpt_tos}")
        print("Message data:\n")
        for line in envelope.content.decode('utf8', errors='replace').splitlines():
            print(f"> {line}".strip())
        print()
        print("End of message")
        return '250 Message accepted for delivery'

# make email from example output from grading.py
file = Path('./email_test/BrendanMurphybm13805.txt')
msg = make_email(file)

# test "make_email" locally
# controller = Controller(ExampleHandler())
# controller.start()
# client = Client(controller.hostname, controller.port)
# client.send_message(msg)
# controller.stop()

# test using "email trap"
config = configparser.ConfigParser()
config.read("smtp.ini")
mailtrap = config['gmail']
with smtp_server(mailtrap, use_ssl=True) as server:
    server.send_message(msg)