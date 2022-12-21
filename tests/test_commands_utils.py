import gzip
import json

import pytest

from manga_recsys.commands.utils import write_df, write_df_per_uid


@pytest.fixture(scope="session")
def test_df(spark):
    return spark.createDataFrame(
        [
            ("a", "b", 1),
            ("a", "c", 2),
            ("a", "d", 3),
            ("b", "e", 4),
            ("b", "f", 5),
            ("b", "g", 6),
        ],
        ["uid", "item", "rating"],
    ).cache()


def test_write_df(test_df, tmp_path):
    write_df(test_df, tmp_path / "test_df")
    assert len(list(tmp_path.glob("*.parquet"))) == 1
    assert len(list(tmp_path.glob("*.json"))) == 1
    # assert directory has only these two files
    assert len(list(tmp_path.glob("*"))) == 2


@pytest.mark.parametrize("compress", [True, False])
def test_write_df_per_uid(test_df, tmp_path, compress):
    output = tmp_path / "test_df_per_uid"
    write_df_per_uid(test_df, output, "uid", compress=compress, parallelism=2)
    # assert these json files are the only files in the directory
    assert len(list(output.glob("*"))) == 2
    paths = list(output.glob("*.json"))
    assert len(paths) == 2
    for path in paths:
        # load the json file
        if compress:
            data = json.loads(gzip.decompress(path.read_bytes()).decode())
        else:
            data = json.loads(path.read_text())

        # uid column should be the name of the path stem
        uid = path.stem
        # assert that the uid is the same for all rows
        assert all([row["uid"] == uid for row in data])
        # assert that it has more that one row
        assert len(data) > 1
