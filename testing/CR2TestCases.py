import pytest
import requests
import os
from dotenv import load_dotenv

'''
This class contains the test cases of the CR_2: Create a Web Service
'''


class CR2TestCases:

    @pytest.fixture
    def repo(self):
        return 'https://github.com/microsoft/QuantumKatas'

    @pytest.fixture
    def pat(self):
        load_dotenv()
        return os.getenv('SECRET_PAT')

    @pytest.fixture
    def user(self):
        return 'UDRE54ED12'

    def test_tc_wse_1_1(self, repo, pat, user):
        r = requests.get(
            f'http://localhost:5001/getSmells?repo={repo}&pat={pat}&user={user}')
        assert r.status_code == 200

    def test_tc_wse_1_2(self, repo, pat):
        r = requests.get(
            f'http://localhost:5001/getSmells?repo={repo}&pat={pat}')
        assert r.status_code == 200

    def test_tc_wse_1_3(self, repo, pat, user):
        r = requests.get(
            f'http://localhost:5001/getSmells?repo={repo}&user={user}')
        assert r.status_code == 400

    def test_tc_wse_1_4(self, pat, user):
        r = requests.get(
            f'http://localhost:5001/getSmells?pat={pat}&user={user}')
        assert r.status_code == 400
