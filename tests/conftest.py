import pytest

from manga_recsys.spark import get_spark


@pytest.fixture(scope="session")
def spark():
    return get_spark(cores=2, memory="2g", partitions=4)
