import json
from pathlib import Path

import pytest

from apgmx import ConfigLoader


@pytest.fixture(scope="session")
def confLoaderFixture():
    return ConfigLoader()


def test_conf_loader_repr(confLoaderFixture: ConfigLoader):
    assert isinstance(confLoaderFixture, ConfigLoader)


def test_ensure_config(confLoaderFixture: ConfigLoader):
    root = Path(__file__).parents[1]
    confLoaderFixture.ensure_config()
    try:
        with open(root.joinpath("apgmx_config.json"), "r") as f:
            jsonRes = json.loads(f.read())
            assert jsonRes["database_uri"] is None or isinstance(
                jsonRes["database_uri"], str
            )
    except FileNotFoundError:
        return


def test_load_data(confLoaderFixture: ConfigLoader):
    assert isinstance(confLoaderFixture.load_data(), dict)


def test_load_env(confLoaderFixture: ConfigLoader):
    assert confLoaderFixture.loadEnv() is True


def test_get_database_uri(confLoaderFixture: ConfigLoader):
    assert isinstance(confLoaderFixture.get_database_uri(), str)
