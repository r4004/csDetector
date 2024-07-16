from statistics import mean, stdev
import os
import csv


def output_statistics(idx: int, data: list, metric: str, outputDir: str):

    # validate
    if len(data) < 1:
        return

    # calculate and output
    stats = calculate_stats(data)

    # output
    with open(os.path.join(outputDir, f"results_{idx}.csv"), "a", newline="") as f:
        w = csv.writer(f, delimiter=",")

        for key in stats:
            outputValue(w, metric, key, stats)


def calculate_stats(data):

    stats = dict(
        count=len(data),
        mean=mean(data),
        stdev=stdev(data) if len(data) > 1 else None
    )

    return stats


def outputValue(w, metric: str, name: str, dict: dict):
    value = dict[name]
    name = "{0}_{1}".format(metric, name)
    w.writerow([name, value])
