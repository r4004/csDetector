from datetime import datetime
import json
import time
import requests
import math

from typing import List
from configuration import Configuration


def get_toxicity_percentage(config: Configuration, comments: List):

    if config.googleKey is None:
        return 0
    # comment out to pause toxicity analysis
    # return 0

    # estimate completion
    qps_limit = 1
    buffer = 5
    query_limit = (qps_limit * 60) - buffer

    toxicity_minutes = math.ceil(len(comments) / query_limit)
    print(
        f"    Toxicity per comment, expecting around {toxicity_minutes} minute(s) completion time",
        end="",
    )

    # declare toxicity results store
    toxic_results = 0

    # wait until the next minute
    sleep_until_next_minute()

    # run analysis
    for idx, comment in enumerate(comments):

        # build request
        url = (
            "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
            + "?key="
            + config.googleKey
        )
        data_dict = {
            "comment": {"text": comment},
            "languages": ["en"],
            "requestedAttributes": {"TOXICITY": {}},
        }

        # send request
        response = requests.post(url=url, data=json.dumps(data_dict))

        # parse response
        response_data = json.loads(response.content)

        try:
            toxicity = float(
                response_data["attributeScores"]["TOXICITY"]["summaryScore"]["value"]
            )
        except:
            print()
            e = response_data["error"]
            raise Exception(f'Error {e["code"]} {e["status"]}: {e["message"]}')

        # add to results store if toxic
        if toxicity >= 0.5:
            toxic_results += 1

        print(".", end="")

        # we are only allowed 1 QPS, wait for a minute
        if (idx + 1) % query_limit == 0:
            print()
            print("        QPS limit reached, napping", end="")
            sleep_until_next_minute()
            print(", processing", end="")

    print()

    # calculate percentage of toxic comments
    percentage = 0 if len(comments) == 0 else toxic_results / len(comments)

    return percentage


def sleep_until_next_minute():
    t = datetime.now()
    sleeptime = 60 - (t.second + t.microsecond / 1000000.0)
    time.sleep(sleeptime)