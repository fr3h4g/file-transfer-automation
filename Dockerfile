FROM python:3.10

WORKDIR /app

COPY pyproject.toml .

COPY ./filetransferautomation /app/filetransferautomation

RUN pip3.10 install .

CMD [ "python" ,"-m", "filetransferautomation" ]