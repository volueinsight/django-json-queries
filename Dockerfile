FROM python:3.6-alpine

RUN pip install tox django==1.11.3

ADD . /code/
WORKDIR /code
