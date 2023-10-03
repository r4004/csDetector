import os
import git
from matplotlib.figure import Figure
import networkx as nx
import csv
import matplotlib.pyplot as plt

from git.objects import Commit
from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from networkx.algorithms import core
from networkx.algorithms.community import greedy_modularity_communities
from progress.bar import Bar
from collections import Counter
from utils import author_id_extractor
from statsAnalysis import output_statistics
from configuration import Configuration

import cadocsLogger

logger = cadocsLogger.get_cadocs_logger(__name__)


def centrality_analysis(
    commits: List[Commit],
    delta: relativedelta,
    batch_dates: List[datetime],
    config: Configuration,
):
    core_devs = list()

    # work with batched commits
    for idx, batchStartDate in enumerate(batch_dates):
        batch_end_date = batchStartDate + delta

        batch = [
            commit
            for commit in commits
            if batchStartDate <= commit.committed_datetime < batch_end_date
        ]

        batch_core_devs = process_batch(idx, batch, config)
        core_devs.append(batch_core_devs)

    return core_devs


def process_batch(batch_idx: int, commits: List[Commit], config: Configuration):
    all_related_authors = {}
    author_commits = Counter({})

    # for all commits...
    logger.info("Analyzing centrality")
    for commit in Bar("Processing").iter(commits):
        author = author_id_extractor(commit.author)

        # increase author commit count
        author_commits.update({author: 1})

        # initialize dates for related author analysis
        commit_date = datetime.fromtimestamp(commit.committed_date)
        earliest_date = commit_date + relativedelta(months=-1)
        latest_date = commit_date + relativedelta(months=+1)

        commit_related_commits = filter(
            lambda c: find_related_commits(
                author, earliest_date, latest_date, c), commits
        )

        commit_related_authors = set(
            list(map(lambda c: author_id_extractor(
                c.author), commit_related_commits))
        )

        # get current related authors collection and update it
        author_related_authors = all_related_authors.setdefault(author, set())
        author_related_authors.update(commit_related_authors)

    return prepare_graph(
        all_related_authors, author_commits, batch_idx, "commitCentrality", config
    )


def build_graph_ql_network(batchIdx: int, batch: list, prefix: str, config: Configuration):
    all_related_authors = {}
    author_items = Counter({})

    # for all commits...
    logger.info("Analyzing centrality")
    for authors in batch:

        for author in authors:

            # increase author commit count
            author_items.update({author: 1})

            # get current related authors collection and update it
            related_authors = set(
                relatedAuthor
                for otherAuthors in batch
                for relatedAuthor in otherAuthors
                if author in otherAuthors and relatedAuthor != author
            )
            author_related_authors = all_related_authors.setdefault(
                author, set())
            author_related_authors.update(related_authors)

    prepare_graph(all_related_authors, author_items, batchIdx, prefix, config)


def prepare_graph(
    all_related_authors: dict,
    author_items: Counter,
    batch_idx: int,
    output_prefix: str,
    config: Configuration,
):

    # prepare graph
    logger.info("Preparing NX graph")
    graph = nx.Graph()

    for author in all_related_authors:
        graph.add_node(author)

        for related_author in all_related_authors[author]:
            graph.add_edge(author.strip(), related_author.strip())

    # analyze graph
    closeness = dict(nx.closeness_centrality(graph))
    betweenness = dict(nx.betweenness_centrality(graph))
    centrality = dict(nx.degree_centrality(graph))
    density = nx.density(graph)
    modularity = []

    try:
        for idx, community in enumerate(greedy_modularity_communities(graph)):
            author_count = len(community)
            community_commit_count = sum(
                author_items[author] for author in community)
            row = [author_count, community_commit_count]
            modularity.append(row)
    except ZeroDivisionError:
        # not handled
        pass

    # finding high centrality authors
    high_centrality_authors = list(
        [author for author, centrality in centrality.items() if centrality > 0.5]
    )

    number_high_centrality_authors = len(high_centrality_authors)

    percentage_high_centrality_authors = number_high_centrality_authors / len(
        all_related_authors
    )

    # calculate TFN
    tfn = len(author_items) - number_high_centrality_authors

    # calculate TFC
    tfc = sum(author_items[author]
              for author in high_centrality_authors) / sum(author_items.values()) * 100

    logger.info("Outputting CSVs")

    # output non-tabular results
    with open(
        os.path.join(config.resultsPath, f"results_{batch_idx}.csv"), "a", newline=""
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow([f"{output_prefix}_Density", density])
        w.writerow([f"{output_prefix}_Community Count", len(modularity)])
        w.writerow([f"{output_prefix}_TFN", tfn])
        w.writerow([f"{output_prefix}_TFC", tfc])

    # output community information
    with open(
        os.path.join(config.metricsPath,
                     f"{output_prefix}_community_{batch_idx}.csv"),
        "a",
        newline="",
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["Community Index", "Author Count", "Item Count"])
        for idx, community in enumerate(modularity):
            w.writerow([idx + 1, community[0], community[1]])

    # combine centrality results
    combined = {}
    for key in closeness:
        single = {
            "Author": key,
            "Closeness": closeness[key],
            "Betweenness": betweenness[key],
            "Centrality": centrality[key],
        }

        combined[key] = single

    # output tabular results
    with open(
        os.path.join(config.metricsPath,
                     f"{output_prefix}_centrality_{batch_idx}.csv"),
        "w",
        newline="",
    ) as f:
        w = csv.DictWriter(
            f, ["Author", "Closeness", "Betweenness", "Centrality"])
        w.writeheader()

        for key in combined:
            w.writerow(combined[key])

    # output high centrality authors
    with open(
        os.path.join(config.resultsPath, f"results_{batch_idx}.csv"), "a", newline=""
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(
            [f"{output_prefix}_NumberHighCentralityAuthors",
                number_high_centrality_authors]
        )
        w.writerow(
            [
                f"{output_prefix}_PercentageHighCentralityAuthors",
                percentage_high_centrality_authors,
            ]
        )

    # output statistics
    output_statistics(
        batch_idx,
        [value for key, value in closeness.items()],
        f"{output_prefix}_Closeness",
        config.resultsPath,
    )

    output_statistics(
        batch_idx,
        [value for key, value in betweenness.items()],
        f"{output_prefix}_Betweenness",
        config.resultsPath,
    )

    output_statistics(
        batch_idx,
        [value for key, value in centrality.items()],
        f"{output_prefix}_Centrality",
        config.resultsPath,
    )

    output_statistics(
        batch_idx,
        [community[0] for community in modularity],
        f"{output_prefix}_CommunityAuthorCount",
        config.resultsPath,
    )

    output_statistics(
        batch_idx,
        [community[1] for community in modularity],
        f"{output_prefix}_CommunityAuthorItemCount",
        config.resultsPath,
    )

    # output graph
    logger.info("Outputting graph")
    plt.figure(5, figsize=(30, 30))

    nx.draw(
        graph,
        with_labels=True,
        node_color="orange",
        node_size=4000,
        edge_color="black",
        linewidths=2,
        font_size=20,
    )

    plt.savefig(
        os.path.join(config.resultsPath, f"{output_prefix}_{batch_idx}.pdf")
    )

    nx.write_graphml(
        graph, os.path.join(config.resultsPath,
                            f"{output_prefix}_{batch_idx}.xml")
    )

    return high_centrality_authors


# helper functions
def find_related_commits(author, earliest_date, latest_date, commit):
    is_different_author = author != author_id_extractor(commit.author)
    if not is_different_author:
        return False

    commit_date = datetime.fromtimestamp(commit.committed_date)
    is_in_range = earliest_date <= commit_date <= latest_date
    return is_in_range
