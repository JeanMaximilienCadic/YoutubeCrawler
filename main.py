from pytube import YouTube
from datetime import timedelta
import xml.etree.ElementTree as ET
import json

class YoutubeCaptionParser(dict):
    def __init__(self, video_id):
        super(YoutubeCaptionParser, self).__init__()
        yt = YouTube(url="https://www.youtube.com/watch?v={}".format(video_id))
        details = yt.player_response['videoDetails']
        self["id"] = video_id
        self["cr"] = yt.player_config_args['cr']
        self["host_language"] = yt.player_config_args['host_language']
        self["channel_id"] = details['channelId']
        self["author"] = details['author']
        self["duration"] = str(timedelta(seconds=int(yt.length)))
        self["captions"] = {}
        try:
            caption_xml = yt.captions.lang_code_index['a.ja'].xml_captions
            for entry in ET.fromstring(caption_xml):
                self["captions"][eval(entry.attrib["start"])] = {
                        "text": entry.text,
                        "stop": eval(entry.attrib["start"])+eval(entry.attrib["dur"])
                    }

            self["neighbors"] = list(set([id[:11] for id in yt.watch_html.split("watch?v=")[1:]]))
        except:
            pass

def crawler(root_id):
    video = YoutubeCaptionParser(video_id=root_id)
    old = set(list([video["id"]]))
    new = set(video["neighbors"]).difference(old)
    results = {}
    while len(new)>0:
        video_id = new.pop()
        old.add(video_id)
        try:
            video = YoutubeCaptionParser(video_id=video_id)
            new = new.union(set(video["neighbors"])).difference(old)
            results[video_id] = video
        except:
            pass

        print(len(old), len(new), len(results))
        if len(results)==100:
            json.dump(results, open("results.json", "w"), ensure_ascii=False, indent=4)
            break


if __name__ == "__main__":
    root_id = "v4MrAyRTWqw"
    crawler(root_id)