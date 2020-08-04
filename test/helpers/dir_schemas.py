from os import fspath
from pathlib import Path
from typing import Any, Dict

def create_dir(path: str,
               dir_dict: Dict[str, Any],
               all_diff_contents: bool = False,
               seed: str = "") -> None:
    """ Creates a directory in the specified path

    :param path: Path to create directory in
    :param dir_dict: Specification of contents to create in directory
    """

    for f in dir_dict["files"]:
        fp = Path(path) / f
        if all_diff_contents:
            fp.write_text(f"{fp}{seed}")
        else:
            fp.touch()

    for contents in dir_dict["subdirs"]:
        subdir_path = Path(path) / contents["dirname"]
        subdir_path.mkdir()

        create_dir(subdir_path,
                   contents,
                   all_diff_contents=all_diff_contents,
                   seed=seed)


# TODO: Bring them under one identifier or something
def multiple_subdir_levels(path: str):
    p = Path(path)
    pattern = {
        "dirname": p.name,
        "fullpath": fspath(p),
        "files": {"one"},
        "subdirs": [{
            "dirname": "sublevel1",
            "fullpath": fspath(p/"sublevel1"),
            "files": {"file1.txt", "file2.tsk"},
            "subdirs": [{
                "dirname": "sublevel2",
                "fullpath": fspath(p/"sublevel1"/"sublevel2"),
                "files": {"ugh.js", "ayy.css", "nope.html"},
                "subdirs": [{
                    "dirname": "Secret Pictures",
                    "fullpath": fspath(p/"sublevel1"/"sublevel2"/"Secret Pictures"),
                    "files": {"SECRET.png"},
                    "subdirs": []
                }]
            },
                {
                "dirname": "Pictures",
                "fullpath": fspath(p/"sublevel1"/"Pictures"),
                "files": {"img1.jpg", "img2.jpg", "vid1.mp4"},
                "subdirs": []
            }]
        }]
    }

    return pattern

