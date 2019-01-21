FROM python:3.6-alpine

RUN adduser -D flaskuser

ADD . /home/flaskuser

WORKDIR /home/flaskuser

RUN which python

RUN pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:$PORT wsgi