# syntax=docker/dockerfile:1
FROM python:3.8-alpine
FROM ubuntu

ARG DEBIAN_FRONTEND=noninteractive

LABEL name regex
LABEL src "https://github.com/cwirks01/regex.git"
LABEL desc "A modifiable regualr expression text excrator tool for a web deployment."

WORKDIR /usr/nginx/html

ENV FLASK_APP=wsgi.py
ENV FLASK_RUN_HOST=0.0.0.0

# Update aptitude with new repo
RUN apt-get update

# Install software
RUN apt-get install -y git && \
    apt-get install -y python3-pip && \
    apt-get install -y python3-tk && \
    apt-get install -y vim && \
    pip3 install -U pip setuptools wheel && \
    pip install blis

# Create known_hosts
# Add github key
# Authorize SSH Host
RUN mkdir -p /regex/ssh && \
    mkdir -p /regex/logs && \
    chmod 0700 /regex/ssh && \
    touch /regex/ssh/known_hosts && \
    touch /regex/ssh/config && \
    touch /.bashrc && \
    touch /etc/ssh/sshd_config && \
    ssh-keyscan -H github.com > /regex/ssh/known_hosts

# RUN echo "127.0.0.1 testing-dev.dev www.testing-dev.dev" >> /etc/hosts 

# Add the keys and set permissions
# RUN echo "Host github.com\n\tStrictHostKeyChecking no\n" >> /regex/ssh/config

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# RUN pip3 install -U pip setuptools wheel &&\
#     pip3 install -U spacy && \
#     python3 -m spacy download en_core_web_sm

COPY . .

EXPOSE 8080
