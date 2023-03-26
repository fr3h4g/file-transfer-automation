FROM python:3.10

LABEL org.opencontainers.image.source="https://github.com/fr3h4g/file-transfer-automation"
LABEL org.opencontainers.image.description="File Transport Automation"

WORKDIR /app

COPY pyproject.toml .

COPY ./filetransferautomation /app/filetransferautomation

RUN pip3.10 install .

CMD [ "python" ,"-m", "filetransferautomation" ]