from requests import Request, post, get, Response
import time
import os
import pdb
import numpy as np
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))


class Istio:
    def __init__(self, 
                 metric: str, 
                 svc_name: str, 
                 host: str = "http://localhost:9090",
                 version: str = None,
                 code: str = None,
                 span: str = "10m",
                 ts: int = int(time.time()),
                 interval: int = 2):
        self.metric = metric
        self.svc_name = svc_name
        self.host = host
        self.version = version
        self.code = code
        self.span = span
        self.ts = ts

    def query(self) -> dict:
        if self.code and self.version:
            query_str = f'{self.metric}{{destination_app="{self.svc_name}", destination_version="{self.version}", response_code="{self.code}"}}[{self.span}]'
        elif self.code:
            query_str = f'{self.metric}{{destination_app="{self.svc_name}", response_code="{self.code}"}}[{self.span}]'
        elif self.version:
            query_str = f'{self.metric}{{destination_app="{self.svc_name}", destination_version="{self.version}"}}[{self.span}]'
        else:
            query_str = f'{self.metric}{{destination_app="{self.svc_name}"}}[{self.span}]'
        res = get(f"{self.host}/api/v1/query", params={
            "query": query_str,
            "time": self.ts
        })
        print(query_str, self.ts)
        res_data = res.json()["data"]["result"]
        res_data = [item["values"] for item in res_data]
        if len(res_data) == 0:
            return res_data
        elif len(res_data) == 1:
            result = [[int(item[0]), eval(item[1])] for item in res_data[0]]
        else:
            result = res_data[0]
            for i in range(1, len(res_data)):
                result = self.sequence_add(result, res_data[i])
        for i in range(len(result)-1, 0, -1):
            result[i][1] = result[i][1] - result[i-1][1]
        result = result[1:]
        return result

    def sequence_add(self, seq1, seq2):
        seq1, seq2 = dict(seq1), dict(seq2)
        result = seq1.copy() if len(seq1) > len(seq2) else seq2.copy()
        for k in result:
            if k in seq1 and k in seq2:
                result[k] = (eval(seq1[k]) if isinstance(seq1[k], str) else seq1[k]) + int(eval(seq2[k]))
            elif k in seq1:
                result[k] = (eval(seq1[k]) if isinstance(seq1[k], str) else seq1[k])
            else:
                result[k] = eval(seq2[k])
        result = [[k, v] for k, v in result.items()]
        return result


class IstioData(Istio):
    def __init__(self, *args, **kwargs):
        super(IstioData, self).__init__(*args, **kwargs)
        self.interval = kwargs["interval"]

        self.output_dir = os.path.join(PROJECT_PATH, 
                                       "data", 
                                       f"{self.svc_name}{'_'+self.version if self.version else ''}")
        self.img_output_dir = os.path.join(PROJECT_PATH,
                                           "img",
                                           f"{self.svc_name}{'_'+self.version if self.version else ''}")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(self.img_output_dir):
            os.makedirs(self.img_output_dir)
        self.file_name = os.path.join(self.output_dir, f"{self.code if self.code else self.metric}.csv")
        self.image_name = os.path.join(self.img_output_dir, f"{self.code if self.code else self.metric}.png")

    def run(self):
        self.data = self.query()
        if self.metric == "istio_request_duration_milliseconds_sum":
            metric = self.metric
            self.metric = "istio_requests_total"
            data = self.query()
            result = []
            for i in range(len(list(zip(self.data, data)))):
                result.append([self.data[i][0], self.data[i][1]/(data[i][1] + 1e-6)])
            self.data = result
            self.metric = metric
        if len(self.data) > 0:
            with open(self.file_name, "a") as fp:
                for ts, val in self.data:
                    print(ts, val, sep=",", file=fp)  
        self.plot()
        
    def plot(self):
        data = np.asarray(self.data)
        if data.size == 0: return
        ts = data[:, 0]
        ts = np.asarray([int(eval(item)) if isinstance(item, str) else item for item in ts])
        val = data[:, 1]
        val = np.asarray([item for item in val])
        sort_args = np.argsort(ts)
        ts = ts[sort_args]
        val = val[sort_args]
        try:
            ts = [datetime.fromtimestamp(item) for item in ts]
        except Exception:
            print(ts)

        plt.figure(self.svc_name, figsize=(20, 5))
        plt.title(self.svc_name)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=self.interval))
        plt.plot(ts, val)
        plt.savefig(self.image_name, bbox_inches="tight")
        plt.close()

