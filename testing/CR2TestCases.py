import pytest
import requests
import os
from dotenv import load_dotenv

'''
This class contains the test cases of the CR_2: Create a Web Service
'''


class Test:

    @pytest.fixture
    def link(self):
        return 'http://localhost:5000/getSmells'

    @pytest.fixture
    def repo(self):
        return 'https://github.com/microsoft/QuantumKatas'

    @pytest.fixture
    def branch(self):
        return 'main'

    @pytest.fixture
    def pat(self):
        load_dotenv()
        return os.getenv('SECRET_PAT')

    def test_tc_wse_1_1(self, link, repo, branch, pat):
        r = requests.get(
            f'{link}?repo={repo}&branch={branch}&pat={pat}')
        assert r.status_code == 200

    def test_tc_wse_1_2(self, link, repo, branch):
        r = requests.get(
            f'{link}?repo={repo}&branch={branch}')
        assert r.status_code == 400

    def test_tc_wse_1_3(self, link, repo, pat):
        r = requests.get(
            f'{link}?repo={repo}&pat={pat}')
        assert r.status_code == 400

    def test_tc_wse_1_4(self, link, branch, pat):
        r = requests.get(
            f'{link}?branch={branch}&pat={pat}')
        assert r.status_code == 400
