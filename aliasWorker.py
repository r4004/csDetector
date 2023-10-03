import os
import git
import yaml

from typing import List
from progress.bar import Bar
from utils import author_id_extractor
from configuration import Configuration

import cadocsLogger

logger = cadocsLogger.get_cadocs_logger(__name__)


def replace_aliases(commits: List[git.Commit], config: Configuration):

    logger.info("Cleaning aliased authors")
    # build path
    alias_path = os.path.join(config.repositoryPath, "aliases.yml")

    # quick lowercase and trim if no alias file
    if alias_path is None or not os.path.exists(alias_path):
        return commits

    # read aliases
    content = ""
    with open(alias_path, "r", encoding="utf-8-sig") as file:
        content = file.read()

    aliases = yaml.load(content, Loader=yaml.FullLoader)

    # transpose for easy replacements
    transposesAliases = {}
    for alias in aliases:
        for email in aliases[alias]:
            transposesAliases[email] = alias

    # replace all author aliases with a unique one
    return replace_all(commits, transposesAliases)


def replace_all(commits, aliases):
    for commit in Bar("Processing").iter(list(commits)):
        copy = commit
        author = author_id_extractor(commit.author)

        if author in aliases:
            copy.author.email = aliases[author]

        yield copy
