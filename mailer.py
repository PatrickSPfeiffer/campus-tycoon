import os
import smtplib
from email.message import EmailMessage

import streamlit as st

import logic


def read_settings():
    settings = {}
    for name in ("EMAIL_ADDRESS", "EMAIL_APP_PASSWORD"):
        value = os.environ.get(name, "")
        if not value:
            try:
                value = st.secrets.get(name, "")
            except FileNotFoundError:
                value = ""
        settings[name] = value
    return settings


def send_result_email(player, final, smtp_factory=smtplib.SMTP_SSL):
    try:
        try:
            content = logic.result_email_message(player, final)
        except ValueError:
            return "failed"

        settings = read_settings()
        address = settings["EMAIL_ADDRESS"]
        password = settings["EMAIL_APP_PASSWORD"]
        if not address or not password:
            return "skipped"

        message = EmailMessage()
        message["From"] = address
        message["To"] = player
        message["Subject"] = content["subject"]
        message.set_content(content["body"])

        with smtp_factory("smtp.gmail.com", 465, timeout=10) as server:
            server.login(address, password)
            server.send_message(message)
        return "sent"
    except (smtplib.SMTPException, OSError):
        return "failed"
    except Exception:
        # Keep unexpected configuration, validation, or message errors private too.
        return "failed"
