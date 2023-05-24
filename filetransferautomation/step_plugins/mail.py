"""Workspace plugin."""
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import logging
import os
from pathlib import Path
import smtplib

from pydantic import BaseModel

from filetransferautomation import settings
from filetransferautomation.common import compare_filter
from filetransferautomation.logs import add_file_log_entry
from filetransferautomation.plugin_collection import Plugin


class Input(BaseModel):
    """Input data model."""

    file_filter: str | None = "*.*"
    delete_files: bool | None = False
    from_address: str | None = ""
    to_addresses: list[str] | list = []
    subject: str | None = ""
    body: str | None = ""


class Output(BaseModel):
    """Output data model."""

    found_files: list[str]
    matched_files: list[str]
    mailed_files: list[str] | None


def send_mail(
    send_from: str,
    send_to: list[str],
    subject: str,
    message: str,
    files: list[str] = [],
):
    """Send mail."""
    msg = MIMEMultipart()
    msg["From"] = send_from
    msg["To"] = ", ".join(send_to)
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = subject

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase("application", "octet-stream")
        with open(path, "rb") as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", f"attachment; filename={format(Path(path).name)}"
        )
        msg.attach(part)

    smtp = smtplib.SMTP(settings.SMTP_HOSTNAME, settings.SMTP_PORT)
    if settings.SMTP_TLS:
        smtp.starttls()
    if settings.SMTP_USERNAME:
        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    smtp.send_message(msg)
    smtp.quit()


class SendFiles(Plugin):
    """Send mail with files."""

    input_model = Input
    output_model = Output
    arguments = input_model

    def process(self):
        """Send mail with files."""
        workspace_directory = self.get_variable("workspace_directory")
        files_to_mail = []
        files = []
        mailed_files = []

        if not self.arguments.from_address:
            return None
        if not self.arguments.to_addresses:
            return None
        if not self.arguments.subject:
            return None
        if not self.arguments.body:
            return None

        files = os.listdir(workspace_directory)
        for file in files:
            if compare_filter(file, self.arguments.file_filter):
                files_to_mail.append(file)

        if files_to_mail:
            send_mail(
                self.arguments.from_address,
                self.arguments.to_addresses,
                self.arguments.subject,
                self.arguments.body,
                files_to_mail,
            )

            for file in files_to_mail:
                mailed_files.append(file)
                size = os.path.getsize(os.path.join(workspace_directory, file))

                add_file_log_entry(
                    task_run_id=self.get_variable("workspace_id"),
                    task_id=self.get_variable("task_id"),
                    step_id=self.get_variable("step_id"),
                    filename=file,
                    status="mailed",
                    filesize=size,
                )

            logging.info(
                f"Mailed files {mailed_files} to: '{self.arguments.to_addresses}'."
            )

            if self.arguments.delete_files:
                for file in mailed_files:
                    os.remove(os.path.join(workspace_directory, file))

        self.set_variable("found_files", files)
        self.set_variable("matched_files", files_to_mail)
        self.set_variable("mailed_files", mailed_files)
