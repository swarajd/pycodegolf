FROM python:3.8-slim-buster

RUN useradd agent

COPY agent.py /home/agent/

USER agent
WORKDIR /home/agent/
