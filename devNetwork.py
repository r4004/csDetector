import sys
import os
import platform
import subprocess
import shutil
import stat
import git
import pkg_resources
import sentistrength
import csv
import pandas as pd

from configuration import parse_dev_network_args
from repoLoader import get_repo
from aliasWorker import replace_aliases
from commitAnalysis import commit_analysis
import centralityAnalysis as centrality
from tagAnalysis import tagAnalysis
from devAnalysis import devAnalysis
from graphqlAnalysis.releaseAnalysis import releaseAnalysis
from graphqlAnalysis.prAnalysis import prAnalysis
from graphqlAnalysis.issueAnalysis import issueAnalysis
from smellDetection import smell_detection
from politenessAnalysis import politeness_analysis
from custmException import customException
from dateutil.relativedelta import relativedelta
import cadocsLogger


logger = cadocsLogger.get_cadocs_logger(__name__)
if platform.system() == "Windows":
    FILEBROWSER_PATH = os.path.join(os.getenv("WINDIR"), "explorer.exe")
else:
    FILEBROWSER_PATH = "open"


communitySmells = [
    {"acronym": "OSE", "name": "Organizational Silo Effect"},
    {"acronym": "BCE", "name": "Black-cloud Effect"},
    {"acronym": "PDE", "name": "Prima-donnas Effect"},
    {"acronym": "SV", "name": "Sharing Villainy"},
    {"acronym": "OS", "name": "Organizational Skirmish"},
    {"acronym": "SD", "name": "Solution Defiance "},
    {"acronym": "RS", "name": "Radio Silence"},
    {"acronym": "TF", "name": "Truck Factor Smell"},
    {"acronym": "UI", "name": "Unhealthy Interaction"},
    {"acronym": "TC", "name": "Toxic Communication"},
]


# This is the actual target of the adapter pattern, which means has the functionality we need
def devNetwork(argv):
    try:
        
        # calling the method for validate the prerequisites of csDetector
        validate()

        # parse args
        config = parse_dev_network_args(argv)
        # prepare folders
        if os.path.exists(config.resultsPath):
            remove_tree(config.resultsPath)

        os.makedirs(config.metricsPath)

        # get repository reference
        repo = get_repo(config)

        # setup sentiment analysis
        senti = sentistrength.PySentiStr()

        senti_jar_path = os.path.join(
            config.sentiStrengthPath, "SentiStrength.jar").replace("\\", "/")
        senti.setSentiStrengthPath(senti_jar_path)

        senti_data_path = os.path.join(
            config.sentiStrengthPath, "SentiStrength_Data").replace("\\", "/") + "/"
        senti.setSentiStrengthLanguageFolderPath(senti_data_path)

        # prepare batch delta
        delta = relativedelta(months=+config.batchMonths)

        # handle aliases
        commits = list(replace_aliases(repo.iter_commits(), config))

        # run analysis
        batch_dates, author_info_dict, days_active = commit_analysis(
            senti, commits, delta, config
        )

        tagAnalysis(repo, delta, batch_dates, days_active, config)

        core_devs = centrality.centrality_analysis(
            commits, delta, batch_dates, config)

        releaseAnalysis(commits, config, delta, batch_dates)

        pr_participant_batches, pr_comment_batches = prAnalysis(
            config,
            senti,
            delta,
            batch_dates,
        )

        testFormatt = {}
        testResult = []
        testConfig = None
        
        issue_participant_batches, issue_comment_batches, excep = issueAnalysis(
            config,
            senti,
            delta,
            batch_dates,
        )

        if excep:
            return testFormatt, testResult, testConfig, excep
        
        if not pr_comment_batches:
            custom_exception = customException("ERROR, There are no comments in pullRequest", 890) 
            return testFormatt, testResult, testConfig, custom_exception.to_json()


        politeness_analysis(config, pr_comment_batches, issue_comment_batches)

        result = {}
        for batchIdx, batchDate in enumerate(batch_dates):

            # get combined author lists
            combined_authors_in_batch = (
                pr_participant_batches[batchIdx] +
                issue_participant_batches[batchIdx]
            )

            # build combined network
            centrality.build_graph_ql_network(
                batchIdx,
                combined_authors_in_batch,
                "issuesAndPRsCentrality",
                config,
            )

            # get combined unique authors for both PRs and issues
            unique_authors_in_pr_batch = set(
                author for pr in pr_participant_batches[batchIdx] for author in pr
            )

            unique_authors_in_issue_batch = set(
                author for pr in issue_participant_batches[batchIdx] for author in pr
            )

            unique_authors_in_batch = unique_authors_in_pr_batch.union(
                unique_authors_in_issue_batch
            )

            # get batch core team
            batch_core_devs = core_devs[batchIdx]

            # run dev analysis
            devAnalysis(
                author_info_dict,
                batchIdx,
                unique_authors_in_batch,
                batch_core_devs,
                config,
            )

            # run smell detection
            detected_smells = smell_detection(config, batchIdx)

            # building a dictionary of detected community smells for each batch analyzed
            result["Index"] = batchIdx
            result["StartingDate"] = batchDate.strftime("%m/%d/%Y")

            # separating smells and converting in their full name
            for index, smell in enumerate(detected_smells):
                if index != 0:
                    smell_name = "Smell" + str(index)
                    result[smell_name] = [smell, get_community_smell_name(detected_smells[index])]
            add_to_smells_dataset(config, batchDate.strftime("%m/%d/%Y"), detected_smells)

        excep = None
        return result, detected_smells, config, excep

    except ValueError as message:
        raise ValueError(message)
    except Exception as error:
        if str(error).__contains__("401"):
            logger.error("The PAT could be wrong or have reached the maximum number of requests. See https://docs.github.com/en/graphql/overview/resource-limitations for more information")
        else:
            logger.error("Exception DEV NETWORK - %s", str(error))

    finally:
        # close repo to avoid resource leaks
        if "repo" in locals():
            del repo



# converting community smell acronym in full name


def get_community_smell_name(smell):
    for sm in communitySmells:
        if sm["acronym"] == smell:
            return sm["name"]
    return smell

# collecting execution data into a dataset

def add_to_smells_dataset(config, starting_date, detected_smells):
    with pd.ExcelWriter('./communitySmellsDataset.xlsx', engine="openpyxl", mode='a', if_sheet_exists="overlay") as writer:
        dataframe = pd.DataFrame(index=[writer.sheets['dataset'].max_row],
                                 data={'repositoryUrl': [config.repositoryUrl],
                                       'repositoryName': [config.repositoryName],
                                       'repositoryAuthor': [config.repositoryOwner],
                                       'startingDate': [starting_date],
                                       'OSE': [str(detected_smells.count('OSE'))],
                                       'BCE': [str(detected_smells.count('BCE'))],
                                       'PDE': [str(detected_smells.count('PDE'))],
                                       'SV': [str(detected_smells.count('SV'))],
                                       'OS': [str(detected_smells.count('OS'))],
                                       'SD': [str(detected_smells.count('SD'))],
                                       'RS': [str(detected_smells.count('RS'))],
                                       'TFS': [str(detected_smells.count('TFS'))],
                                       'UI': [str(detected_smells.count('UI'))],
                                       'TC': [str(detected_smells.count('TC'))]
                                       })
        dataframe.to_excel(writer, sheet_name="dataset",
                           startrow=writer.sheets['dataset'].max_row, header=False)


class Progress(git.remote.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
        logger(self._cur_line, end="\r")


def commitDate(tag):
    return tag.commit.committed_date


def remove_readonly(fn, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    remove_tree(path)


def remove_tree(path):
    if os.path.isdir(path):
        shutil.rmtree(path, onerror=remove_readonly)
    else:
        os.remove(path)


# https://stackoverflow.com/a/50965628
def explore(path):
    # explorer would choke on forward slashes
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, "/select,", os.path.normpath(path)])
        

# validate the installation pre-requisites of the tool
def validate():
    # validate running in venv
        if not hasattr(sys, "prefix"):
            raise Exception(
                "The tool does not appear to be running in the virtual environment!\nSee README for activation."
            )

        # validate python version
        if sys.version_info.major != 3 or sys.version_info.minor != 8:
            raise Exception(
                "Expected Python 3.8 as runtime but got {0}.{1}, the tool might not run as expected!\nSee README for stack requirements.".format(
                    sys.version_info.major,
                    sys.version_info.minor,
                    sys.version_info.micro,
                )
            )

        # validate installed modules
        required = {
            "wheel",
            "networkx",
            "pandas",
            "matplotlib",
            "gitpython",
            "requests",
            "pyyaml",
            "progress",
            "strsimpy",
            "python-dateutil",
            "sentistrength",
            "joblib",
        }
        installed = {pkg for pkg in pkg_resources.working_set.by_key}
        missing = required - installed

        if len(missing) > 0:
            raise Exception(
                "Missing required modules: {0}.\nSee README for tool installation.".format(
                    missing
                )
            )
