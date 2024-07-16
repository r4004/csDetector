import os
import argparse
from typing import Sequence
from urllib.parse import urlparse


class Configuration:
    def __init__(
        self,
        repositoryUrl: str,
        batchMonths: int,
        outputPath: str,
        sentiStrengthPath: str,
        maxDistance: int,
        pat: str,
        googleKey: str,
        startDate: str,
        endDate: str
    ):
        self.repositoryUrl = repositoryUrl
        self.batchMonths = batchMonths
        self.outputPath = outputPath
        self.sentiStrengthPath = sentiStrengthPath
        self.maxDistance = maxDistance
        self.pat = pat
        self.googleKey = googleKey
        self.startDate = startDate
        self.endDate = endDate

        # parse repo name into owner and project name
        split = self.repositoryUrl.split("/")
        self.repositoryOwner = split[3]
        self.repositoryName = split[4]

        # build repo path
        self.repositoryPath = os.path.join(self.outputPath, split[3], split[4])

        # build results path
        self.resultsPath = os.path.join(self.repositoryPath, "results")

        # build metrics path
        self.metricsPath = os.path.join(self.resultsPath, "metrics")


def parse_alias_args(args: Sequence[str]):

    parser = argparse.ArgumentParser(
        description="Extract commit author aliases from GitHub repositories.",
        epilog="Check README file for more information on running this tool.",
    )

    parser.add_argument(
        "-p",
        "--pat",
        help="GitHub PAT (personal access token) used for querying the GitHub API",
        required=True,
    )

    parser.add_argument(
        "-r",
        "--repositoryUrl",
        help="GitHub repository URL that you want to analyse",
        required=True,
    )

    parser.add_argument(
        "-d",
        "--maxDistance",
        help="""string distance metric
        https://github.com/luozhouyang/python-string-similarity#metric-longest-common-subsequence
        """,
        type=float,
        required=True,
    )

    parser.add_argument(
        "-o",
        "--outputPath",
        help="local directory path for analysis output",
        required=True,
    )

    parser.add_argument(
        "-sd",
        "--startDate",
        help="start date of project life",
        required=False,
    )

    args = parser.parse_args()
    config = Configuration(
        args.repositoryUrl, 0, args.outputPath, "", args.maxDistance, args.pat, ""
    )

    return config


def parse_dev_network_args(args: Sequence[str]):

    parser = argparse.ArgumentParser(
        description="Perform network and statistical analysis on GitHub repositories.",
        epilog="Check README file for more information on running this tool.",
    )

    parser.add_argument(
        "-p",
        "--pat",
        help="GitHub PAT (personal access token) used for querying the GitHub API",
        required=True,
    )

    parser.add_argument(
        "-g",
        "--googleKey",
        help="Google Cloud API Key used for authentication with the Perspective API",
        required=False,
    )

    parser.add_argument(
        "-r",
        "--repositoryUrl",
        help="GitHub repository URL that you want to analyse",
        required=True,
    )

    parser.add_argument(
        "-m",
        "--batchMonths",
        help="Number of months to analyze per batch. Default=9999",
        type=float,
        default=9999,
    )

    parser.add_argument(
        "-s",
        "--sentiStrengthPath",
        help="local directory path to the SentiStregth tool",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--outputPath",
        help="Local directory path for analysis output",
        required=True,
    )

    parser.add_argument(
        "-sd",
        "--startDate",
        help="Start date of project life",
        required=False,
    )

    parser.add_argument(
        "-ed",
        "--endDate",
        help="End date of project life",
        required=False,
    )

    args = parser.parse_args(args)

    #validation of the input inserted by the user
    if args.repositoryUrl is None:
        raise ValueError("The repository URL is needed")

    if "github" not in urlparse(args.repositoryUrl).netloc:
        raise ValueError("The repository URL inserted is not valid or malformed")

    if args.pat is None:
        raise ValueError("A valid Github PAT is needed to clone the repository")

    senti_files_found = False

    if args.sentiStrengthPath is None:
        raise ValueError("A valid senti folder is needed to perform sentiment analysis on the repository")

    try:
        with os.scandir(args.sentiStrengthPath) as entries:
            for entry in entries:
                if "SentiStrength" in entry.name:
                    senti_files_found = True
                    break
        if not senti_files_found:
            raise ValueError("The senti folder provided does not contains the needed files. Check the README for more "
                             "details")
    except FileNotFoundError:
        raise ValueError("A malformed or invalid senti folder is provided")

    try:
        os.makedirs("out/output_default")
    except Exception as e:
        pass

    if args.outputPath is None:
        raise ValueError("A valid output folder is needed to save the analysis of the repository")

    try:
        with os.scandir(args.outputPath) as entries:
            pass
    except FileNotFoundError:
        raise ValueError("The output folder provided is not avaiable in the file system or have restricted access")

    config = Configuration(
        args.repositoryUrl,
        args.batchMonths,
        args.outputPath,
        args.sentiStrengthPath,
        0,
        args.pat,
        args.googleKey,
        args.startDate,
        args.endDate
    )

    return config
