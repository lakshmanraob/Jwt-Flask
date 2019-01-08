FROM python:3.6-alpine

RUN adduser -D flaskuser

ADD . /home/flaskuser

WORKDIR /home/flaskuser

RUN pip install -r requirements.txt

ENTRYPOINT python run.py