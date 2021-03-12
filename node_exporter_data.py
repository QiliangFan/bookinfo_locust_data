from requests import Response, Request, get
import os
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import pdb


def sequence_add(seq1, seq2):
    seq1, seq2 = dict(seq1), dict(seq2)
    result = seq1.copy() if len(seq1) > len(seq2) else seq2.copy()
    for k in result:
        if k in seq1 and k in seq2:
            result[k] = (eval(seq1[k]) if isinstance(seq1[k], str) else seq1[k]) + eval(seq2[k])
        elif k in seq1:
            result[k] = (eval(seq1[k]) if isinstance(seq1[k], str) else seq1[k])
        else:
            result[k] = eval(seq2[k])
    result = [[k, v] for k, v in result.items()]
    return result

def query_node(host, metric, span):
    res = get(f"{host}/api/v1/query", params={
        "query": f"{metric}[{span}]"
    }).json()
    print(res.keys(), f"({metric})[{span}]")
    data = res["data"]["result"]
    res_data = [item["values"] for item in data]
    if len(res_data) == 0:
        return res_data
    elif len(res_data) == 1:
        result = [[int(item[0]), eval(item[1])] for item in res_data[0]]
    else:
        result = res_data[0]
        for i in range(1, len(res_data)):
            result = sequence_add(result, res_data[i])
    return result


class NodeDataCum:
    def __init__(self, metric_name: str, value1: list, value2: list):
        """
        (ts, val)
        """
        self.metric_name = metric_name
        self.value1 = value1
        self.value2 = value2
        assert len(self.value1) == len(self.value2), \
                f"expected value1 and value2 have the same length, but got {len(self.value1)} and {len(self.value2)}"

    def make_delta(self) -> None:
        for i in range(len(self.value1)-1, 0):
            self.value1[i][1] = self.value1[i][1] - self.value1[i-1][1]
            if self.metric_name == "mem_usage":
                self.value1[i][1] = self.value2[i][1] - self.value1[i][1]
            else:
                self.value2[i][1] = self.value2[i][1] - self.value2[i-1][1]
        self.value1 = self.value1[1:]
        self.value2 = self.value2[1:]

    def div(self) -> None:
        self.value = []
        for v1, v2 in zip(self.value1, self.value2):
            if v2[1] <= 0:
                self.value.append([v1[0], 0])
            else:
                self.value.append([v1[0], v1[1]/v2[1]])

    def save(self, save_dir):
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        with open(os.path.join(save_dir, f"{self.metric_name}.csv"), "w") as fp:
            for ts, v in self.value:
                print(ts, v, sep=",", file=fp)

    def plot(self, save_dir, interval=2):
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        img_file = os.path.join(save_dir, f"{self.metric_name}.png")
        vals = np.asarray(self.value)
        ts = vals[:, 0]
        vals = vals[:, 1]
        ts = np.asarray([int(eval(v)) if isinstance(v, str) else v for v in ts])
        vals = np.asarray([eval(v) if isinstance(v, str) else v for v in vals])
        sort_args = np.argsort(ts)
        ts = ts[sort_args]
        vals = vals[sort_args]
        ts = [datetime.fromtimestamp(t) for t in ts]

        plt.figure(self.metric_name, figsize=(20, 5))
        plt.title(self.metric_name)
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=interval))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H"))
        plt.plot(ts, vals)
        plt.savefig(img_file, bbox_inches="tight")
        plt.close()


class NodeData:
    def __init__(self, metric_name, value):
        self.metric_name = metric_name
        self.value = value
        self.interval = int(self.value[1][0] - self.value[0][0])

    def save(self, save_dir):
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        with open(os.path.join(save_dir, f"{self.metric_name}.csv"), "w") as fp:
            for ts, v in self.value:
                print(ts, v, sep=",", file=fp)

    def plot(self, save_dir, interval=2):
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        img_file = os.path.join(save_dir, f"{self.metric_name}.png")
        vals = np.asarray(self.value)
        ts = vals[:, 0]
        vals = vals[:, 1]
        ts = np.asarray([int(eval(v)) if isinstance(v, str) else v for v in ts])
        vals = np.asarray([eval(v) if isinstance(v, str) else v for v in vals])
        sort_args = np.argsort(ts)
        ts = ts[sort_args]
        vals = vals[sort_args]
        ts = [datetime.fromtimestamp(t) for t in ts]
        
        plt.figure(self.metric_name, figsize=(10, 5))
        plt.title(self.metric_name)
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=interval))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H"))
        plt.plot(ts, vals)
        plt.savefig(img_file, bbox_inches="tight")
        plt.close()