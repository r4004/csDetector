import os
import csv
import convokit

import statsAnalysis as stats
from custmException import customException
from configuration import Configuration


def politeness_analysis(
    config: Configuration,
    prCommentBatches: list,
    issueCommentBatches: list,
):
    calculate_accl(config, prCommentBatches, issueCommentBatches)

    calculate_rpc(config, "PR", prCommentBatches)
    calculate_rpc(config, "Issue", prCommentBatches)


def calculate_accl(config, pr_comment_batches, issue_comment_batches):
    for batch_idx, batch in enumerate(pr_comment_batches):

        pr_comment_lengths = list([len(c) for c in batch])
        issue_comment_batch = list([len(c)
                                 for c in issue_comment_batches[batch_idx]])


        if(len(issue_comment_batch) == 0 or len(pr_comment_lengths) == 0):
            issue_comment_lengths_mean = 0
            pr_comment_lengths_mean = 0
        else:
            pr_comment_lengths_mean = stats.calculate_stats(pr_comment_lengths)["mean"]
            issue_comment_lengths_mean = stats.calculate_stats(issue_comment_batch)["mean"]

        accl = pr_comment_lengths_mean + issue_comment_lengths_mean / 2

        # output results
        with open(os.path.join(config.resultsPath, f"results_{batch_idx}.csv"),
                  "a",
                  newline=""
                  ) as f:
            w = csv.writer(f, delimiter=",")
            w.writerow([f"ACCL", accl])


def calculate_rpc(config, output_prefix, comment_batches):
    for batch_idx, batch in enumerate(comment_batches):

        # analyze batch
        positive_marker_count = get_results(batch)

        # output results
        with open(
            os.path.join(config.resultsPath, f"results_{batch_idx}.csv"),
            "a",
            newline="",
        ) as f:
            w = csv.writer(f, delimiter=",")
            w.writerow([f"RPC{output_prefix}", positive_marker_count])


def get_results(comments: list):

    # define default speaker
    speaker = convokit.Speaker(id="default", name="default")

    # build utterance list
    utterances = list(
        [
            convokit.Utterance(id=str(idx), speaker=speaker, text=comment)
            for idx, comment in enumerate(comments)
        ]
    )

    myException = customException(utterances,"utterances")
    myException.printError()

    # build corpus
    corpus = convokit.Corpus(utterances=utterances)

    # parse
    parser = convokit.TextParser(verbosity=1000)
    corpus = parser.transform(corpus)

    # extract politeness features
    politeness = convokit.PolitenessStrategies()
    corpus = politeness.transform(corpus, markers=True)
    features = corpus.get_utterances_dataframe()

    # get positive politeness marker count
    positive_marker_count = sum(
        [
            feature["feature_politeness_==HASPOSITIVE=="]
            for feature in features["meta.politeness_strategies"]
        ]
    )

    return positive_marker_count
