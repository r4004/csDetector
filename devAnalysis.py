import os
import csv

from configuration import Configuration

import cadocsLogger

logger = cadocsLogger.get_cadocs_logger(__name__)


def devAnalysis(
    authorInfoDict: set, batchIdx: int, devs: set, coreDevs: set, config: Configuration
):

    # select experienced developers
    experienced_devs = [
        login
        for login, author in authorInfoDict.items()
        if author["experienced"] == True
    ]

    # filter by developers present in list of aliased developers by commit
    number_active_experienced_devs = len(devs.intersection(set(experienced_devs)))

    # calculate bus factor
    bus_factor = (len(devs) - len(coreDevs)) / len(devs)

    # calculate TFC
    commit_count = sum(
        [author["commitCount"] for login, author in authorInfoDict.items()]
    )
    sponsored_commit_count = sum(
        [
            author["commitCount"]
            for login, author in authorInfoDict.items()
            if author["sponsored"] == True
        ]
    )
    experienced_commit_count = sum(
        [
            author["commitCount"]
            for login, author in authorInfoDict.items()
            if author["experienced"] == True
        ]
    )

    sponsored_tfc = sponsored_commit_count / commit_count * 100
    experienced_tfc = experienced_commit_count / commit_count * 100

    logger.info("Writing developer analysis results")
    with open(
        os.path.join(config.resultsPath, f"results_{batchIdx}.csv"), "a", newline=""
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["NumberActiveExperiencedDevs",
                   number_active_experienced_devs])
        w.writerow(["BusFactorNumber", bus_factor])
        w.writerow(["SponsoredTFC", sponsored_tfc])
        w.writerow(["ExperiencedTFC", experienced_tfc])
