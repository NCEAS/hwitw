FROM ubuntu:20.04

RUN apt update && \
    apt install -y python3 python3-pip

RUN pip install parsl

