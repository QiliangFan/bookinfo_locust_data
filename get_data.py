from typing import Tuple
import requests
from requests import Response, get, post
import argparse
from tqdm import tqdm
import json
import os
import pdb
from multiprocessing import Pool
from time import time

def get_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--metric", type=str, required=True, help="the metric to be collected.")
    argparser.add_argument("--code", type=int, required=False, default=None)
    argparser.add_argument("--time", type=int, required=False, default=int(time()))
    argparser.add_argument("--span", type=str, required=False, default="5m")

    argparser.add_argument("--host", type=str, default="http://localhost:9090")

    config = vars(argparser.parse_args())
    return config


def query_data(metric, service, ts, span: str,code=None, version=None) -> Tuple:
    if code and version:
        query = f'{metric}{{destination_app="{service}", destination_version="{version}", response_code="{code}"}}[{span}]'
    elif code:
        query = f'{metric}{{destination_app="{service}", response_code="{code}"}}[{span}]'
    elif version:
        query = f'{metric}{{destination_app="{service}", destination_version="{version}"}}[{span}]'
    else:
        query = f'{metric}{{destination_app="{service}"}}[{span}]'
    res = get(f"{HOST}/api/v1/query", params={
        "query": f"{query}",
        "time": f"{ts}"
    })
    return res.json(), query+".csv"


def main():
    for svc in service_list:
        if isinstance(svc, str):
            svc_name = svc 
            data, filename = query_data(CONFIG["metric"], 
                            svc_name, 
                            ts=CONFIG["time"],
                            span=CONFIG["span"],
                            code=CONFIG["code"],
                    )
            output_file = os.path.join(PROJECT_PATH, "data", filename)
            with open(OUTPUTS_FILE, "a") as fp:
                print(filename, file=fp)
            values = [item["values"] for item in data["data"]["result"]]
            result = []
            for vals in zip(*values):
                v = 0
                ts = 0
                for val in vals:
                    v += eval(val[1])
                    ts = int(val[0])
                result.append([ts, v])
            
            with open(output_file, "a") as fp:
                for ts, v in result:
                    print(ts, v, sep=",", file=fp)
        else:
            for svc_name, versions in svc.items():
                for ver in versions:
                    data, filename = query_data(CONFIG["metric"], 
                                    svc_name, 
                                    ts=CONFIG["time"],
                                    span=CONFIG["span"],
                                    code=CONFIG["code"],
                                    version=ver
                            ) 
                    output_file = os.path.join(PROJECT_PATH, "data", filename)  
                    with open(OUTPUTS_FILE, "a") as fp:
                        print(filename, file=fp)
                    values = [item["values"] for item in data["data"]["result"]]
                    result = []
                    for vals in zip(*values):
                        v = 0
                        ts = 0
                        for val in vals:
                            # pdb.set_trace()
                            v += eval(val[1])
                            ts = int(val[0])
                        result.append([ts, v])
                    with open(output_file, "a") as fp:
                        for ts, v in result:
                            print(ts, v, sep=",", file=fp)

if __name__ == "__main__":
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    CONFIG = get_args()
    HOST = CONFIG["host"].rstrip("/")

    service_list = json.load(open(os.path.join(PROJECT_PATH, "service_config.json"), "rb"))

    # output directory
    out_dir = os.path.join(PROJECT_PATH, "data")
    if not os.path.exists(out_dir): os.makedirs(out_dir)

    OUTPUTS_FILE = os.path.join(PROJECT_PATH, "data", "output.txt")
    main()