import pytest
import os
import pandas as pd
from dotenv import load_dotenv
from configuration import Configuration
from csDetectorAdapter import CsDetectorAdapter
from devNetwork import add_to_smells_dataset

'''
This class contains the test cases of the CR_1: Refactoring I/O
'''


class Test:
    load_dotenv()
    SECRET_PAT = os.getenv('SECRET_PAT')

    @pytest.fixture
    def example_config(self):
        return Configuration(
            "https://github.com/test/testRepository",
            "master",
            None,
            "testOutputPath",
            None,
            None,
            None,
            None,
            None

        )

    @pytest.fixture
    def example_starting_date(self):
        return "24/05/2022 00:26:00"

    @pytest.fixture
    def example_detected_smells(self):
        return ["OSE",
                "SV",
                "UI",
                "UI"]

    @pytest.fixture
    def path(self):
        return os.getcwd() + '\communitySmellsDataset.xlsx'

    # CR_1-SSC

    def test_tc_ssc_1_1(self, example_config, example_detected_smells, example_starting_date, path):
        max_row_in_excel = 0
        with pd.ExcelWriter('./communitySmellsDataset.xlsx', engine="openpyxl", mode="a",
                            if_sheet_exists="overlay") as writer:
            dataframe = pd.DataFrame(index=[writer.sheets['dataset'].max_row],
                                     data={'repositoryUrl': [example_config.repositoryUrl],
                                           'repositoryName': [example_config.repositoryName],
                                           'repositoryAuthor': [example_config.repositoryOwner],
                                           'startingDate': [example_starting_date],
                                           'OSE': [str(example_detected_smells.count('OSE'))],
                                           'BCE': [str(example_detected_smells.count('BCE'))],
                                           'PDE': [str(example_detected_smells.count('PDE'))],
                                           'SV': [str(example_detected_smells.count('SV'))],
                                           'OS': [str(example_detected_smells.count('OS'))],
                                           'SD': [str(example_detected_smells.count('SD'))],
                                           'RS': [str(example_detected_smells.count('RS'))],
                                           'TFS': [str(example_detected_smells.count('TFS'))],
                                           'UI': [str(example_detected_smells.count('UI'))],
                                           'TC': [str(example_detected_smells.count('TC'))]
                                           })
            dataframe.to_excel(writer, sheet_name="dataset",
                               startrow=writer.sheets['dataset'].max_row, header=False)
            max_row_in_excel = writer.sheets['dataset'].max_row

        add_to_smells_dataset(example_config, example_starting_date,
                              example_detected_smells, os.getcwd() + '\communitySmellsDataset.xlsx')

        df = pd.read_excel(io="./communitySmellsDataset.xlsx", sheet_name='dataset')

        are_row_equals = True
        # controllo tutte le colonne delle ultime due righe
        for x in range(1, df.iloc[max_row_in_excel - 1].size):
            if df.iloc[max_row_in_excel - 1][x] != df.iloc[max_row_in_excel - 2][x]:
                are_row_equals = False

        assert are_row_equals

    def test_tc_ssc_1_2(self, example_config, example_starting_date, path):
        with pytest.raises(AttributeError):
            add_to_smells_dataset(example_config, example_starting_date, None, path)

    def test_tc_ssc_1_3(self, example_config, example_detected_smells, path):

        max_row_in_excel = 0
        with pd.ExcelWriter('./communitySmellsDataset.xlsx', engine="openpyxl", mode="a",
                            if_sheet_exists="overlay") as writer:
            max_row_in_excel = writer.sheets['dataset'].max_row

        add_to_smells_dataset(example_config, None,
                              example_detected_smells, path)  # controllare che la data sul file non è valorizzata
        df = pd.read_excel(io="./communitySmellsDataset.xlsx", sheet_name='dataset')

        assert df.iloc[max_row_in_excel - 1]['startingDate'] != df.iloc[max_row_in_excel - 1]['startingDate']

    def test_tc_ssc_1_4(self, example_detected_smells, example_starting_date, path):
        with pytest.raises(AttributeError):
            add_to_smells_dataset(None, example_starting_date, example_detected_smells, path)

    # CR_1-ATE

    # gitRepository, branch, gitPAT, startingDate="null", sentiFolder="./senti", outputFolder="./out"

    def test_tc_ate_1_1(self):
        tool = CsDetectorAdapter()
        tool.executeTool(gitRepository="https://github.com/tensorflow/ranking",
                         branch="master",
                         gitPAT=self.SECRET_PAT,
                         #startingDate="2022-05-27",
                         outputFolder="../output",
                         sentiFolder="../senti")

    def test_tc_ate_1_2(self):
        with pytest.raises(ValueError) as err:
            tool = CsDetectorAdapter()
            tool.executeTool("https://github.com/nuri22/csDetector",
                             "master",
                             self.SECRET_PAT,
                             "26/05/2022",
                             "./senti",
                             "arcimboldo")
            assert "The output folder provided is not available in the file system or have restricted access" in err.value

    def test_tc_ate_1_3(self):
        with pytest.raises(ValueError) as err:
            tool = CsDetectorAdapter()
            tool.executeTool("https://github.com/nuri22/csDetector",
                             "master",
                             self.SECRET_PAT,
                             "26/05/2022",
                             "./senti",
                             None)
            assert "A valid output folder is needed to save the analysis of the repository" in err.value

    def test_tc_ate_1_4(self):
        try:
            with pytest.raises(ValueError) as err:
                tool = CsDetectorAdapter()
                os.mkdir("./arcimboldo")
                tool.executeTool("https://github.com/nuri22/csDetector",
                                 "master",
                                 self.SECRET_PAT,
                                 "26/05/2022",
                                 "./arcimboldo",
                                 "./output")
                assert "The senti folder provided does not contains the needed files. Check the README for more details" in err.value
        finally:
            os.rmdir("./arcimboldo")

    def test_tc_ate_1_5(self):
        try:
            with pytest.raises(ValueError) as err:
                tool = CsDetectorAdapter()
                os.mkdir("./arcimboldo")
                tool.executeTool("https://github.com/nuri22/csDetector",
                                 "master",
                                 self.SECRET_PAT,
                                 "26/05/2022",
                                 "pappappero",
                                 "./output")
                assert "A malformed or invalid senti folder is provided" in err.value
        finally:
            os.rmdir("./arcimboldo")

    def test_tc_ate_1_6(self):
        with pytest.raises(ValueError) as err:
            tool = CsDetectorAdapter()
            tool.executeTool("https://github.com/nuri22/csDetector",
                             "master",
                             self.SECRET_PAT,
                             "26/05/2022",
                             None,
                             "./output")

            assert "A valid senti folder is needed to perform sentiment analysis on the repository" in err.value

    def test_tc_ate_1_7(self):
        with pytest.raises(ValueError) as err:
            tool = CsDetectorAdapter()
            tool.executeTool("https://github.com/nuri22/csDetector",
                             "master",
                             None,
                             "26/05/2022",
                             "./senti",
                             "./output")
            assert "A valid Github PAT is needed to clone the repository" in err.value

    def test_tc_ate_1_8(self):
        with pytest.raises(ValueError) as err:
            tool = CsDetectorAdapter()
            tool.executeTool("Io amo il testing",
                             "master",
                             self.SECRET_PAT,
                             "26/05/2022",
                             "./senti",
                             "./output")
            assert "The repository URL inserted is not valid or malformed" in err.value

    def test_tc_ate_1_9(self):
        with pytest.raises(ValueError) as err:
            tool = CsDetectorAdapter()
            tool.executeTool(None,
                             "master",
                             self.SECRET_PAT,
                             "26/05/2022",
                             "./senti",
                             "./output")
            assert "The repository URL is needed" in err.value