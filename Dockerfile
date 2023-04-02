FROM python:3.10

LABEL org.opencontainers.image.source="https://github.com/fr3h4g/file-transfer-automation"
LABEL org.opencontainers.image.description="File Transport Automation"

WORKDIR /app

COPY . /app

RUN pip3.10 install -e .

RUN mkdir /data /data/work /data/folders /data/scripts

COPY ./data/scripts /data/scripts

CMD [ "file-transfer-automation" ]