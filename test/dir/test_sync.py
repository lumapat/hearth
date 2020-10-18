import pytest # type: ignore

from hearth.dir.data import Dir, loaded_dir


# Test no sync for identical directories
# Test basic sync (add-only) for
#   - Only files
#   - Files and a single subdir with files
#   - Nested subdirs with files
#   - One nested subdir and one with only files

def test_placeholder():
    pass