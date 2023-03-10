#! /usr/bin/python3
import argparse
import smtplib
from smtplib import SMTP as Client
import configparser
from email.message import EmailMessage
from contextlib import contextmanager
from pathlib import Path
import ssl
import time

from grading import get_id

FROM = "MATH10017.homework.feedback@gmail.com"

# TODO add progress bar and maybe add reminder email to yourself that this lab was emailed to students

def make_email(file, subject="MATH10017 homework feedback"):
    msg = EmailMessage()
    msg['From'] = FROM
    msg['Subject'] = subject

    # get email address of form ab12345@bristol.ac.uk
    ID = get_id(file)
    if (ID == None):
        raise ValueError("File name does not contain valid student ID.")
    else:
        msg['To'] = ID + "@bristol.ac.uk"

    # get content for message
    with open(file, 'r', encoding='utf-8') as f:
        msg.set_content(f.read())
    
    return msg

@contextmanager
def smtp_server(smtp_creds, use_ssl=True):
    if use_ssl:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(smtp_creds['host'], smtp_creds['port'], context=context)
    else:
        server = Client(smtp_creds['host'], smtp_creds['port'])
    server.login(smtp_creds['username'], smtp_creds['password'])

    try:
        yield server
    finally:
        server.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("in_dir", type=str, help="directory containing .txt files to email")
    args = parser.parse_args()
    PATH = Path.cwd() / args.in_dir

    files = list(PATH.glob("*.txt"))

    config = configparser.ConfigParser()
    config.read("smtp.ini")
    gmail = config['gmail']

    with smtp_server(gmail, use_ssl=True) as server:
        for file in files:
            msg = make_email(file)
            server.send_message(msg)
            time.sleep(.5)


if __name__ == "__main__":
    main()
