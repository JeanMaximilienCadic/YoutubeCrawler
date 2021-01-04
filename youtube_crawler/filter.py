import json
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import copy
import nagisa

class CaptionFilterer(dict):
    def __init__(self, d, stats):
        super(CaptionFilterer, self).__init__()
        self.captions = copy.deepcopy(d["captions"])
        try:
            self.filter_overlapping()
            self.filter_valid_labels()
            self.filter_durations()
            self.filter_bayesian(stats)
            self.close(d)
        except:
            print(f"Could not process {d['id']}")
            raise Exception
        finally:
            del self.captions

    def filter_overlapping(self):
        # Filter non overlapping sequences
        starts = [eval(start) for start, _ in self.captions.items()]
        stops = [e["stop"] for _, e in self.captions.items()]
        valids = set([starts[k] for k, stop in enumerate(stops[:-1]) if stop<starts[k+1]])
        self.captions = dict([(k, v) for k, v in self.captions.items() if eval(k) in valids])

    def filter_valid_labels(self):
        # Filter valids labels
        labels = json.load(open("data/labels_jp.json", "r"))
        self.captions = dict([(k, self.captions[k]) for k, e in self.captions.items()
                              if len(set(e["text"]).difference(labels))==0])

    def filter_durations(self):
        self.captions = dict([(start, e) for start, e in self.captions.items() if e["dur"] in range(2, 11)])

    def filter_bayesian(self, stats):
        valids=[]
        for _start, e in self.captions.items():
            dur = e["dur"]
            L = len(e["text"].replace(" ", ""))
            x = stats[dur]
            if L in range(max(int(x["mu"]-x["std"]), 2), int(x["mu"]+x["std"])):
                valids.append(_start)
        self.captions = dict([(start, e) for start, e in self.captions.items() if start in valids])

    def close(self, d):
        def tokenize(e):
            e["text"] = " ".join(nagisa.tagging(e["text"].replace(" ", "")).words)
            return e
        d["captions"] = dict([(k, tokenize(e)) for k, e in self.captions.items()])
        for k, v in d.items():
            self.setdefault(k, v)


def main(video_id, d, stats):
    try:
        _d = CaptionFilterer(d, stats)
        assert len(_d["captions"])>1
        bool_result = True
    except:
        bool_result, _d = False, {}
    return bool_result, video_id, _d

class Bayesian(dict):
    def __init__(self, items):
        super(Bayesian, self).__init__()
        X = {}
        with ProcessPoolExecutor() as e:
            fs = [e.submit(self.run, d["captions"]) for _, d in items]
            for f in tqdm(as_completed(fs), total=len(fs), desc="Bayesian filtering"):
                assert f._exception is None
                _X = f._result
                for k, v in _X.items():
                    try:
                        X[k].extend(v)
                    except KeyError:
                        X[k] = v
        [self.setdefault(dur, {"mu": np.mean(values), "std": np.mean(values)}) for dur, values in X.items()]


    @staticmethod
    def run(captions):
        X = {}
        try:
            for start, e in captions.items():
                dur = e["dur"]
                L = len(e["text"].replace(" ", ""))
                try:
                    X[dur].append(L)
                except:
                    X[dur] = [L]
        except:
            pass
        return X

def main_filter():
    ID = "v4MrAyRTWqw"
    results = {}
    items = json.load(open(f"__data__/json/{ID}.json", "r")).items()
    stats = Bayesian(items)
    with ProcessPoolExecutor() as e:
        fs = [e.submit(main, id, d, stats) for id, d in items]
        for f in tqdm(as_completed(fs), total=len(fs), desc="Filtering"):
            assert f._exception is None
            bool_result, id, result = f._result
            if bool_result:
                results[id] = result
    json.dump(results, open(f"__data__/json/{ID}.json", "w"), ensure_ascii=False, indent=4)

if __name__=="__main__":
    main_filter()