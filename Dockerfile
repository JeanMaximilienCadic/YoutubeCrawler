FROM jcadic/python:latest

WORKDIR /tmp

RUN git clone -b add_docker https://github.com/JeanMaximilienCadic/YoutubeCrawler.git

WORKDIR /tmp/YoutubeCrawler

RUN pip install -r requirements.txt && python main.py
