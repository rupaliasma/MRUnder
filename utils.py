import numpy as np


def echoSort(paths):
    echo_times = [float(p.split("EchoTime_")[1]) for p in paths]
    idx = np.argsort(echo_times)
    return [paths[i] for i in idx]