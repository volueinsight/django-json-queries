FROM python:3.6-alpine

RUN pip install tox

ADD . /code/
WORKDIR /code
