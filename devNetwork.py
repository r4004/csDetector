import sys
import os
import subprocess
import shutil
import stat
import git
import pkg_resources
import sentistrength
import csv
import pandas as pd

from configuration import parseDevNetworkArgs
from repoLoader import getRepo
from aliasWorker import replaceAliases
from commitAnalysis import commitAnalysis
import centralityAnalysis as centrality
from tagAnalysis import tagAnalysis
from devAnalysis import devAnalysis
from graphqlAnalysis.releaseAnalysis import releaseAnalysis
from graphqlAnalysis.prAnalysis import prAnalysis
from graphqlAnalysis.issueAnalysis import issueAnalysis
from smellDetection import smellDetection
from politenessAnalysis import politenessAnalysis
from dateutil.relativedelta import relativedelta

FILEBROWSER_PATH = os.path.join(os.getenv("WINDIR"), "explorer.exe")

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

        # parse args
        config = parseDevNetworkArgs(argv)
        # prepare folders
        if os.path.exists(config.resultsPath):
            remove_tree(config.resultsPath)

        os.makedirs(config.metricsPath)

        # get repository reference
        repo = getRepo(config)

        # setup sentiment analysis
        senti = sentistrength.PySentiStr()

        sentiJarPath = os.path.join(
            config.sentiStrengthPath, "SentiStrength.jar").replace("\\", "/")
        senti.setSentiStrengthPath(sentiJarPath)

        sentiDataPath = os.path.join(
            config.sentiStrengthPath, "SentiStrength_Data").replace("\\", "/") + "/"
        senti.setSentiStrengthLanguageFolderPath(sentiDataPath)

        # prepare batch delta
        delta = relativedelta(months=+config.batchMonths)

        # handle aliases
        commits = list(replaceAliases(repo.iter_commits(), config))

        # run analysis
        batchDates, authorInfoDict, daysActive = commitAnalysis(
            senti, commits, delta, config
        )

        tagAnalysis(repo, delta, batchDates, daysActive, config)

        coreDevs = centrality.centralityAnalysis(
            commits, delta, batchDates, config)

        releaseAnalysis(commits, config, delta, batchDates)

        prParticipantBatches, prCommentBatches = prAnalysis(
            config,
            senti,
            delta,
            batchDates,
        )

        issueParticipantBatches, issueCommentBatches = issueAnalysis(
            config,
            senti,
            delta,
            batchDates,
        )

        politenessAnalysis(config, prCommentBatches, issueCommentBatches)
        result = {}
        for batchIdx, batchDate in enumerate(batchDates):

            # get combined author lists
            combinedAuthorsInBatch = (
                prParticipantBatches[batchIdx] +
                issueParticipantBatches[batchIdx]
            )

            # build combined network
            centrality.buildGraphQlNetwork(
                batchIdx,
                combinedAuthorsInBatch,
                "issuesAndPRsCentrality",
                config,
            )

            # get combined unique authors for both PRs and issues
            uniqueAuthorsInPrBatch = set(
                author for pr in prParticipantBatches[batchIdx] for author in pr
            )

            uniqueAuthorsInIssueBatch = set(
                author for pr in issueParticipantBatches[batchIdx] for author in pr
            )

            uniqueAuthorsInBatch = uniqueAuthorsInPrBatch.union(
                uniqueAuthorsInIssueBatch
            )

            # get batch core team
            batchCoreDevs = coreDevs[batchIdx]

            # run dev analysis
            devAnalysis(
                authorInfoDict,
                batchIdx,
                uniqueAuthorsInBatch,
                batchCoreDevs,
                config,
            )

            # run smell detection
            detectedSmells = smellDetection(config, batchIdx)

            # building a dictionary of detected community smells for each batch analyzed
            result["Index"] = batchIdx
            result["StartingDate"] = batchDate.strftime("%m/%d/%Y")

            # separating smells and converting in their full name
            for index, smell in enumerate(detectedSmells):
                if(index != 0):
                    smellName = "Smell" + str(index)
                    result[smellName] = [
                        smell, get_community_smell_name(detectedSmells[index])]
            add_to_smells_dataset(
                config, batchDate.strftime("%m/%d/%Y"), detectedSmells)
        return result, detectedSmells, config


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
        print(self._cur_line, end="\r")


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
