FROM python:3.10

WORKDIR /app

COPY requirements.txt .

COPY ./filetransferautomation /app/filetransferautomation

CMD [ "python" ,"-m", "filetransferautomation" ]