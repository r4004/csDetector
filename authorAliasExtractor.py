import git
import yaml
import os
import requests
import sys
import re

from configuration import Configuration, parse_alias_args
from repoLoader import get_repo
from progress.bar import Bar
from utils import author_id_extractor
from strsimpy.metric_lcs import MetricLCS

import cadocsLogger

logger = cadocsLogger.get_cadocs_logger(__name__)


def main():
    try:
        # parse args
        config = parse_alias_args(sys.argv)

        # get repository reference
        repo = get_repo(config)

        # build path
        alias_path = os.path.join(config.repositoryPath, "aliases.yml")

        # delete existing alias file if present
        if os.path.exists(alias_path):
            os.remove(alias_path)

        # extract aliases
        extract_aliases(config, repo, alias_path)

    finally:
        # close repo to avoid resource leaks
        if "repo" in locals():
            del repo


def extract_aliases(config: Configuration, repo: git.Repo, alias_path: str):
    commits = list(repo.iter_commits())

    # get all distinct author emails
    emails = set(
        author_id_extractor(commit.author) for commit in Bar("Processing").iter(commits)
    )

    # get a commit per email
    shas_by_email = {}
    for email in Bar("Processing").iter(emails):

        commit = next(
            commit
            for commit in repo.iter_commits()
            if author_id_extractor(commit.author) == email
        )

        shas_by_email[email] = commit.hexsha

    # query github for author logins by their commits
    logins_by_email = dict()
    emails_without_logins = []

    for email in Bar("Processing").iter(shas_by_email):
        sha = shas_by_email[email]
        url = "https://api.github.com/repos/{}/{}/commits/{}".format(
            config.repositoryOwner, config.repositoryName, sha
        )
        request = requests.get(
            url, headers={"Authorization": "token " + config.pat})
        commit = request.json()

        if not "author" in commit.keys():
            continue

        if not commit["author"] is None and not commit["author"]["login"] is None:
            logins_by_email[email] = commit["author"]["login"]
        else:
            emails_without_logins.append(email)

    # build initial alias collection from logins
    aliases = {}
    used_as_values = {}

    for email in logins_by_email:
        login = logins_by_email[email]
        alias_emails = aliases.setdefault(login, [])
        alias_emails.append(email)
        used_as_values[email] = login

    if len(emails_without_logins) > 0:
        for authorA in Bar("Processing").iter(emails_without_logins):
            quick_matched = False

            # go through used values
            for key in used_as_values:
                if authorA == key:
                    quick_matched = True
                    continue

                if are_similar(authorA, key, config.maxDistance):
                    alias = used_as_values[key]
                    aliases[alias].append(authorA)
                    used_as_values[authorA] = alias
                    quick_matched = True
                    break

            if quick_matched:
                continue

            # go through already extracted keys
            for key in aliases:
                if authorA == key:
                    quick_matched = True
                    continue

                if are_similar(authorA, key, config.maxDistance):
                    aliases[key].append(authorA)
                    used_as_values[authorA] = key
                    quick_matched = True
                    break

            if quick_matched:
                continue

            # go through all authors
            for authorB in emails_without_logins:
                if authorA == authorB:
                    continue

                if are_similar(authorA, authorB, config.maxDistance):
                    aliased_author = aliases.setdefault(authorA, [])
                    aliased_author.append(authorB)
                    used_as_values[authorB] = authorA
                    break

    logger.info("Writing aliases to '{0}'".format(alias_path))
    if not os.path.exists(os.path.dirname(alias_path)):
        os.makedirs(os.path.dirname(alias_path))

    with open(alias_path, "a", newline="") as f:
        yaml.dump(aliases, f)


def are_similar(valueA: str, valueB: str, maxDistance: float):
    lcs = MetricLCS()
    expr = r"(.+)@"

    local_part_a_matches = re.findall(expr, valueA)
    local_part_b_matches = re.findall(expr, valueB)

    if len(local_part_a_matches) == 0:
        local_part_a_matches = [valueA]

    if len(local_part_b_matches) == 0:
        local_part_b_matches = [valueB]

    distance = lcs.distance(local_part_a_matches[0], local_part_b_matches[0])

    return distance <= maxDistance


main()
