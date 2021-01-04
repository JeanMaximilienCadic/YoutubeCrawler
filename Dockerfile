FROM jcadic/python:latest

WORKDIR /tmp

RUN git clone  https://github.com/JeanMaximilienCadic/YoutubeCrawler.git

WORKDIR /tmp/YoutubeCrawler

ENV PATH /root/anaconda3/envs/py37/bin:$PATH

RUN pip install -r requirements.txt && pip install nagisa 
