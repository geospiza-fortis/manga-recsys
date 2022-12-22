import pytest

from manga_recsys.commands.sync import tar_big_directories, untar_big_directories


def test_tar_big_directories(tmp_path):
    # create a directory struct
    threshold = 10
    num_dirs = 3
    num_toplevel_files = 5

    root = tmp_path / "source"
    root.mkdir(parents=True)
    for i in range(num_dirs):
        (root / f"dir{i}").mkdir()
        for j in range(threshold + 1):
            (root / f"dir{i}" / f"file{j}").touch()
    for i in range(num_toplevel_files):
        (root / f"file{i}").touch()

    # create a directory struct
    output = tmp_path / "output"
    # run the function
    tar_big_directories(root, output, threshold, parallelism=2)

    # check that the output directory has the correct number of files
    assert (
        len([p for p in output.glob("**/*") if p.is_file()])
        == num_dirs + num_toplevel_files
    )

    # now untar the directories into a third directory and check that the
    # original and unpacked directories are the same
    output2 = tmp_path / "output2"
    untar_big_directories(output, output2, parallelism=2)

    # assert the relative path sets are the same
    assert set([p.relative_to(root) for p in root.glob("**/*")]) == set(
        [p.relative_to(output2) for p in output2.glob("**/*")]
    )
