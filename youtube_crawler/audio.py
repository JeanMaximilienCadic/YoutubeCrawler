import os
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm


class YoutubeAudio:
    def __init__(self, video_id, root, sr=16000):
        self.video_id = video_id
        self.url = None
        self.root = root
        self.sr = sr
        self.output_dir = f"{self.root}/{'/'.join(list(self.video_id))}"
        self.audio_filename = f"{self.output_dir}/{self.video_id}.wav"
        self.json_filename = f"{self.output_dir}/{self.video_id}.json"
        if not os.path.exists(self.json_filename):
            try:
                from pytube import YouTube
                yt = YouTube(url="https://www.youtube.com/watch?v={}".format(video_id))
                stream = [s for s in yt.streams.fmt_streams if s.itag==140]
                assert len(stream)==1
                self.url = stream[0].url
            except AssertionError:
                print("Could not get the audio file")

    def slice(self, d):
        def download():
            output_filename = f"/tmp/{self.video_id}.mp4"
            os.system(f"rm {output_filename}") if os.path.exists(output_filename) else None
            os.system(f"rm {self.audio_filename}") if os.path.exists(self.audio_filename) else None
            try:
                os.makedirs(f"{self.output_dir}", exist_ok=True)
                # Download and convert
                os.system(f"wget \"{self.url}\" -O {output_filename}")
                os.system(f"ffmpeg -i {output_filename} -ar {self.sr} {self.audio_filename}")
                assert os.path.exists(self.audio_filename)
            except:
                raise Exception
            finally:
                os.system(f"rm {output_filename}") if os.path.exists(output_filename) else None

        try:
            if os.path.exists(self.json_filename):
                d = json.load(open(self.json_filename, "r"))
            else:
                audio, sr = None, None
                for k, e in d["captions"].items():
                    start, stop = int(eval(k)), int(e["stop"])
                    segment_filename = f"{self.output_dir}/{self.video_id}-{start}_{stop}_{stop-start}.wav"
                    if not os.path.exists(segment_filename):
                        try:
                            import librosa
                            import soundfile as sf
                            download() if not os.path.exists(self.audio_filename) else None
                            audio, _ = librosa.load(self.audio_filename, sr=self.sr) if audio is None else (audio, None)
                            segment = audio[start*self.sr: stop*self.sr]
                            sf.write(segment_filename, segment, self.sr)
                        except:
                            segment_filename = None
                    e["audio_filename"] = segment_filename
                    d["captions"][k]=e
        except:
            pass
        finally:
            # os.system(f"rm {self.audio_filename}") if os.path.exists(self.audio_filename) else None
            self.d = d
        return self.d

    def close(self):
    # if not os.path.exists(self.json_filename):
        json.dump(self.d, open(self.json_filename, "w"), ensure_ascii=False, indent=4)
        # with open("__data__/csv/results.csv", "a") as f:
        #     f.write(f'{self.json_filename}\n')

def main(video_id, d):
    try:
        audio = YoutubeAudio(video_id, root="__data__/audio")
        if (audio.url is not None) or (os.path.exists(audio.json_filename)):
            d = audio.slice(d)
            audio.close()
            return True, video_id, d
        return False, video_id, d
    except:
        with open("__data__/csv/errors.csv", "a") as f:
            f.write(f'{video_id}\n')
        return False, video_id, d

def main_audio():
    ID = "v4MrAyRTWqw"
    items = list(json.load(open(f"__data__/json/{ID}.json", "r")).items())
    results={}
    # excepts = json.load(open("excepts.json", "r"))
    with ProcessPoolExecutor() as e:
        fs = [e.submit(main, id, d) for id, d in items]
        for f in tqdm(as_completed(fs), total=len(fs), desc="Slicing"):
                assert f._exception is None
                bool_result, id, result = f._result
                results[id] = result if bool_result else None
        json.dump(results, open(f"__data__/json/{ID}.json", "w"), ensure_ascii=False, indent=4)

if __name__=="__main__":
    main_audio()