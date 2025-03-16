FROM python:3.9-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .


CMD python3 populate_database.py ; python3 AI_API.py
