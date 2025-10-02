import os

import janetup
import tempfile
with tempfile.TemporaryDirectory() as tempdir:
    dirname = janetup.get_from_github("janet", "janet-lang", tempdir)
    print(dirname)
    assert os.path.isdir(dirname)

with tempfile.TemporaryDirectory() as tempdir:
    dirname = janetup.get_from_github("janet", "janet-lang", tempdir, commit="8fd1672")
    print(dirname)
    assert os.path.isdir(dirname)

with tempfile.TemporaryDirectory() as tempdir:
    dirname = janetup.get_from_github("janet", "janet-lang", tempdir, branch="master")
    print(dirname)
    assert os.path.isdir(dirname)

with tempfile.TemporaryDirectory() as tempdir:
    dirname = janetup.get_from_github("janet", "janet-lang", tempdir, tag="v1.38.0")
    print(dirname)
    assert os.path.isdir(dirname)

with tempfile.TemporaryDirectory() as tempdir:
    dirname = janetup.get_from_github("spork", "janet-lang", tempdir, branch="master")
    print(dirname)
    assert os.path.isdir(dirname)

with tempfile.TemporaryDirectory() as tempdir:
    dirname = janetup.get_from_github("jeep", "pyrmont", tempdir, branch="master")
    print(dirname)
    assert os.path.isdir(dirname)
