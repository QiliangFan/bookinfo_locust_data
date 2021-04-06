import argparse
import json
import os
from time import time
from node_exporter_data import query_node, NodeData, NodeDataCum
import pdb
from data import IstioData
import traceback


def get_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--metric", type=str, required=False,
                           help="the metric to be collected.", default=None)
    argparser.add_argument("--code", type=int, required=False, default=None)
    argparser.add_argument(
        "--ts", type=int, required=False, default=int(time()))
    argparser.add_argument("--span", type=str, required=False, default="5m")
    argparser.add_argument("--host", type=str, default="http://localhost:9090")
    argparser.add_argument("--node_exporter", type=bool, default=False)
    argparser.add_argument("--interval", type=int, required=True)
    config = vars(argparser.parse_args())
    return config


def process_node_exporter_data():
    save_path = os.path.join(PROJECT_PATH, "data", "system_metrics")
    img_path = os.path.join(PROJECT_PATH, "img", "system_metrics")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    for line in NODE_METRICS:
<<<<<<< HEAD
        try:
            line = line.strip()
            metric_name, query = line.split(" ")
            vals = query_node(CONFIG["host"], query,
                              CONFIG["span"], ts=CONFIG["ts"])
            node_data = NodeData(metric_name, vals)
            node_data.save(save_path)
            node_data.plot(img_path, interval=interval)
        except:
            traceback.print_exc()

=======
        line = line.strip()
        metric_name, query = line.split(" ")
        vals = query_node(CONFIG["host"], query, CONFIG["span"], ts=CONFIG["ts"])
        node_data = NodeData(metric_name, vals)
        node_data.save(save_path)
        node_data.plot(img_path, interval=interval)
>>>>>>> 04ac5bea80fd7af418e71edfdfbfcbc74104ceec

def process_node_exporter_data_cum():
    save_path = os.path.join(PROJECT_PATH, "data", "system_metrics")
    img_path = os.path.join(PROJECT_PATH, "img", "system_metrics")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    for line in NODE_METRICS_CUM:
<<<<<<< HEAD
        try:
            line = line.strip()
            metric_name, query1, query2 = line.split(" ")
            val1 = query_node(CONFIG["host"], query1,
                              CONFIG["span"], ts=CONFIG["ts"])
            val2 = query_node(CONFIG["host"], query2,
                              CONFIG["span"], ts=CONFIG["ts"])
            node_data_cum = NodeDataCum(metric_name, val1, val2)
            node_data_cum.make_delta()
            node_data_cum.div()
            node_data_cum.save(save_path)
            node_data_cum.plot(img_path, interval=interval)
        except:
            traceback.print_exc()
=======
        line = line.strip()
        metric_name, query1, query2 = line.split(" ")
        val1 = query_node(CONFIG["host"], query1, CONFIG["span"], ts=CONFIG["ts"])
        val2 = query_node(CONFIG["host"], query2, CONFIG["span"], ts=CONFIG["ts"])
        node_data_cum = NodeDataCum(metric_name, val1, val2)
        node_data_cum.make_delta()
        node_data_cum.div()
        node_data_cum.save(save_path)
        node_data_cum.plot(img_path, interval=interval)
>>>>>>> 04ac5bea80fd7af418e71edfdfbfcbc74104ceec


def main():
    if not CONFIG["node_exporter"]:  # network metrics
        CONFIG.pop("node_exporter")
        for svc in service_list:
            if isinstance(svc, str):
                istio_data = IstioData(svc_name=svc, **CONFIG)
                istio_data.run()
            else:
                for svc_name, versions in svc.items():
                    for version in versions:
                        istio_data = IstioData(
                            svc_name=svc_name, version=version, **CONFIG)
                        istio_data.run()
    else:   # system resources metrics
        process_node_exporter_data()

        process_node_exporter_data_cum()


if __name__ == "__main__":
    PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
    service_list = json.load(
        open(os.path.join(PROJECT_PATH, "service_config.json"), "rb"))
    CONFIG = get_args()
    interval = CONFIG["interval"]
    # pdb.set_trace()
    # node-exporter
    NODE_METRICS = open(os.path.join(PROJECT_PATH, "node_metrics.txt"), "r")
    NODE_METRICS_CUM = open(os.path.join(
        PROJECT_PATH, "node_metrics_cumulative.txt"), "r")

    main()
