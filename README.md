![Youtube Logo](img/youtube.png)
--------------------------------------------------------------------------------

YoutubeCrawler is a Python package that provides a simplified framework based on youtube_dl to download youtube audio and captions easily

## Installation
Simply run the docker-compose file 
```
version: '2.3'

services:
 youtube_crawler:
  image: jcadic/youtube_crawler
  container_name: youtube_crawler
  volumes:
    - "./youtube_crawler/__data__:/tmp/YoutubeCrawler/youtube_crawler/__data__"
  command: tail -F anything
```

By launching the container as a daemon:
```docker-compose up -d```

Then you can run a example and download 10 videos from youtube by running
```
docker exec -it youtube_crawler python main.py
```

