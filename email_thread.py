import json
import threading
from email.message import EmailMessage

from pathlib import Path
import smtplib
import os

DIR = Path(__file__).resolve().parent
SERVER = "SERVER"
EMAIL = "EMAIL"
ID = "ID"
KEY = "KEY"
PASSWORD = "PASSWORD"


class EmailSend(threading.Thread):
    def __init__(self, thread_name, email, subject, body):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.recepient = email
        self.subject = subject
        self.body = body

    def run(self):
        try:
            with open(os.path.join(DIR, "documents", "secret.json")) as secret:
                data = json.load(secret)
                email = data[SERVER][EMAIL][ID]
                password = data[SERVER][EMAIL][KEY]
        except Exception as e:
            print("FILE ERROR : " + str(e))
        else:
            # Build email
            msg = EmailMessage()
            msg.set_content(self.body)
            msg["Subject"] = self.subject
            msg["From"] = email
            msg["To"] = self.recepient

            try:
                email_send_ref = smtplib.SMTP("smtp.gmail.com", 587)
                email_send_ref.starttls()
                email_send_ref.login(email, password)
                email_send_ref.send_message(msg)
                email_send_ref.quit()
            except Exception as e:
                print("EMAIL FAILED : " + str(e))
            else:
                print("EMAIL SENT")
