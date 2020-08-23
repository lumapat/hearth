from os import fspath
from pathlib import Path
from typing import Any, Dict, List


from hearth.dirdiff import Dir


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

    for dirname, contents in dir_dict["subdirs"].items():
        subdir_path = Path(path) / dirname
        subdir_path.mkdir()

        create_dir(subdir_path,
                   contents,
                   all_diff_contents=all_diff_contents,
                   seed=seed)


# TODO: Bring them under one identifier or something
def multiple_subdir_levels(path: str) -> Dir:
    p = Path(path)
    dir = Dir(p.name, fspath(p))
    dir.files = ["one"]

    s1_path = p/"sublevel1"
    sublevel1 = Dir("sublevel1", fspath(s1_path))
    sublevel1.files = {"file1.txt", "file2.tsk"}

    sublevel2 = Dir("sublevel2", fspath(s1_path/"sublevel2"))
    sublevel2.files = {"ugh.js", "ayy.css", "nope.html"}

    secret_pictures = Dir("Secret Pictures", fspath(s1_path/"sublevel2"/"Secret Pictures"))
    secret_pictures.files = {"SECRET.png"}
    sublevel2.subdirs = {secret_pictures.dirname: secret_pictures}

    pictures = Dir("Pictures", fspath(s1_path/"Pictures"))
    pictures.files = {"img1.jpg", "img2.jpg", "vid1.mp4"}

    sublevel1.subdirs = {
        sublevel2.dirname: sublevel2,
        pictures.dirname: pictures
    }

    return dir


def deeply_nested_subdirs(path: str,
                          bottom_files: List[str],
                          num_levels: int = 3) -> Dir:
    p = Path(path)/"subdir1"
    root_dir = Dir("subdir1", fspath(p))

    dir_ptr = root_dir
    for i in range(2, num_levels):
        subdirname = f"subdir{i}"
        p = p/subdirname
        subdir = Dir(
            subdirname,
            fspath(p/subdirname)
        )

        dir_ptr.subdirs = {subdirname: subdir}
        dir_ptr = subdir

    # At the deepest level
    dir_ptr.files = bottom_files

    return root_dir
