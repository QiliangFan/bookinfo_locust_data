import os
from glob import glob
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pdb


def main():
    for svc in SVCS:
        try:
            files_4xx = glob(os.path.join(DATA_DIR, svc, "4*.csv"))
            files_5xx = glob(os.path.join(DATA_DIR, svc, "5*.csv"))
            files_error = []
            files_error.extend(files_4xx), files_error.extend(files_5xx)

            requests_total_file = glob(os.path.join(DATA_DIR, svc, "istio_requests_total.csv"))[0]

            request_total: np.ndarray = pd.read_csv(requests_total_file, header=None).values
            request_error = request_total.copy()
            request_error[:, 1] = 0
            for file in files_error:
                err_val: np.ndarray = pd.read_csv(file, header=None).values
                val_len = len(err_val)
                request_error = request_error[-val_len:]
                request_total = request_total[-val_len:]
                request_error[:, 1] += err_val[:, 1]
            request_error[:, 1] /= request_total[:, 1]
            request_error = np.nan_to_num(request_error, posinf=0, neginf=0)
            data_frame = pd.DataFrame(request_error)
            data_frame.to_csv(os.path.join(DATA_DIR, svc, "error_rate.csv"), header=None, index=False)
            
            # pdb.set_trace()
            ts = request_error[:, 0]
            ts = np.asarray([datetime.fromtimestamp(t) for t in ts])
            vals = request_error[:, 1]

            plt.figure("error_rate", figsize=(20, 5))
            plt.title("error_rate")
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H"))
            plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=interval))
            plt.plot(ts, vals)
            plt.savefig(os.path.join(IMG_DIR, svc, "error_rate.png"), bbox_inches="tight")
            plt.close()
        except:
            pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, required=True)
    config = vars(parser.parse_args())
    interval = config["interval"]

    SVCS = ["details", "productpage", "ratings", "reviews_v1", "reviews_v2", "reviews_v3"]

    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    IMG_DIR = os.path.join(PROJECT_PATH, "img")
    DATA_DIR = os.path.join(PROJECT_PATH, "data")

    main()
