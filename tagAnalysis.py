import os
import git
import csv
import datetime

from progress.bar import Bar
from statsAnalysis import output_statistics
from typing import List
from dateutil.relativedelta import relativedelta
from configuration import Configuration
import cadocsLogger

logger = cadocsLogger.get_cadocs_logger(__name__)


def tagAnalysis(
    repo: git.Repo,
    delta: relativedelta,
    batchDates: List[datetime.datetime],
    daysActive: List[int],
    config: Configuration,
):
    logger.info("Analyzing tags")

    tag_info = []
    logger.info(
        "Sorting (no progress available, may take several minutes to complete)")
    tags = sorted(repo.tags, key=getTaggedDate)

    # get tag list
    if len(tags) > 0:
        last_tag = None
        for tag in Bar("Processing").iter(tags):

            if last_tag is None:
                commit_count = len(
                    list(tag.commit.iter_items(repo, tag.commit)))
            else:
                since_str = formatDate(getTaggedDate(last_tag))
                commit_count = len(
                    list(tag.commit.iter_items(repo, tag.commit, after=since_str))
                )

            tag_info.append(
                dict(
                    path=tag.path,
                    rawDate=getTaggedDate(tag),
                    date=formatDate(getTaggedDate(tag)),
                    commitCount=commit_count,
                )
            )

            last_tag = tag

    # output tag batches
    for idx, batchStartDate in enumerate(batchDates):
        batch_end_date = batchStartDate + delta

        batch_tags = [
            tag
            for tag in tag_info
            if batchStartDate <= tag["rawDate"] < batch_end_date
        ]

        outputTags(idx, batch_tags, daysActive[idx], config)


def outputTags(idx: int, tagInfo: List[dict], daysActive: int, config: Configuration):

    # calculate FN
    fn = len(tagInfo) / daysActive * 100 if daysActive > 0 else 0

    # output non-tabular results
    with open(
        os.path.join(config.resultsPath, f"results_{idx}.csv"), "a", newline=""
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["Tag Count", len(tagInfo)])

    # output tag info
    logger.info("Outputting CSVs")

    with open(
        os.path.join(config.resultsPath, f"results_{idx}.csv"), "a", newline=""
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["FN", fn])

    with open(
        os.path.join(config.metricsPath, f"tags_{idx}.csv"), "a", newline=""
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["Path", "Date", "Commit Count"])
        for tag in tagInfo:
            w.writerow([tag["path"], tag["date"], tag["commitCount"]])

    output_statistics(
        idx,
        [tag["commitCount"] for tag in tagInfo],
        "TagCommitCount",
        config.resultsPath,
    )


def getTaggedDate(tag):
    date = None

    if tag.tag is None:
        date = tag.commit.committed_datetime
    else:

        # get timezone
        offset = tag.tag.tagger_tz_offset
        tzinfo = datetime.timezone(-datetime.timedelta(seconds=offset))

        # get aware date from timestamp
        date = tag.tag.tagged_date
        date = datetime.datetime.fromtimestamp(date, tzinfo)

    return date


def formatDate(value):
    return value.strftime("%Y-%m-%d")
