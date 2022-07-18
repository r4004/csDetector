import os
import git
from os import path
from configuration import Configuration
import cadocsLogger

logger = cadocsLogger.get_cadocs_logger(__name__)


def get_repo(config: Configuration):
    # build path
    repo_path = os.path.join(
        config.repositoryPath,
        "{}.{}".format(config.repositoryOwner, config.repositoryName),
    )
    # get repository reference
    repo = None
    if not os.path.exists(repo_path):
        logger.info("Downloading repository...")
        repo = git.Repo.clone_from(
            config.repositoryUrl,
            repo_path,
            branch="master",
            progress=Progress(),
            odbt=git.GitCmdObjectDB,
        )
        print()
    else:
        repo = git.Repo(repo_path, odbt=git.GitCmdObjectDB)
    return repo


class Progress(git.remote.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
        print(self._cur_line, end="\r")
