import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import tempfile

finish = """
Created new Janet environment at {venv_path}:

(Bash/Zsh)
    run `source {venv_path}/bin/activate` to enter
    the new environment, then `deactivate` to exit.
(Fish)
    run `source {venv_path}/bin/activate.fish` to enter
    the new environment, then `deactivate` to exit.
"""

# waiting for Windows support
#(PowerShell) run `. {venv_path}/bin/activate.ps1` to enter the new environment, then `deactivate` to exit.
#(CMD)        run `{venv_path}\bin\activate` to enter the new environment, then `deactivate` to exit.


def parse_args():
    parser = argparse.ArgumentParser(
        prog='janetup',
        description='Install a custom Janet build, in an isolated environment.')
    parser.add_argument('dirname', help="Directory for new Janet build")
    args = parser.parse_args()
    return args

def get_from_github(name:str, owner:str,
                    temp_dir:str,
                    release:str = None,
                    branch:str = None,
                    tag:str = None,
                    commit:str = None) -> str|None:
    curdir = os.getcwd()
    os.chdir(temp_dir)
    file_name = None
    base_url = f"https://github.com/{owner}/{name}/archive"
    url = None
    message = None
    if branch is None and tag is None and commit is None:  # we are trying to get a release
        # get list of releases
        try:
            urllib.request.urlretrieve(f"https://api.github.com/repos/{owner}/{name}/releases",
                                       "releases.json")
        except urllib.request.HTTPError:
            print(f"Could not download the latest {name} release info.")
            return None

        if os.path.isfile("releases.json"):
            with open("releases.json") as f:
                data = json.load(f)
                releases = [d["tag_name"] for d in data]
                if release is None:
                    tag = releases[0]
                elif release in releases:
                    tag = release
                else:
                    print(f"Could not find the release {release} in {name} releases.")
                    return None
            os.remove("releases.json")
        file_name = f"{tag}.tar.gz"
        url = f"{base_url}/refs/tags/{file_name}"
        message = f"{name} - release:{tag}"

    elif branch is not None:
        file_name = f"{branch}.tar.gz"
        url = f"{base_url}/refs/heads/{file_name}"
        message = f"{name} - branch:{branch}"
    elif tag is not None:
        file_name = f"{tag}.tar.gz"
        url = f"{base_url}/refs/tags/{file_name}"
        message = f"{name} - tag:{tag}"
    elif commit is not None:
        file_name = f"{commit}.tar.gz"
        url = f"{base_url}/{file_name}"
        message = f"{name} - commit:{tag}"

    print(f"Downloading {message}")

    try:
        path, msg = urllib.request.urlretrieve(url, file_name)
    except urllib.request.HTTPError:
        print("Could not download {name} @ {url}.")
        return None

    tar = tarfile.open(file_name)
    outdir = os.path.abspath(f"{name}_git")
    tar.extractall(path=outdir, filter='data')
    tar.close()
    os.remove(file_name)

    os.chdir(outdir)
    files = glob.glob(f"{name}*")
    if len(files) == 0:
        print(f"Could not find {name} @ {url}.")
        return None

    outdir = os.path.abspath(files[0])

    os.chdir(curdir)
    return outdir


def build_janet(tempdir, dirname):
    curdir = os.getcwd()
    os.chdir(tempdir)
    print(f"Building Janet, PREFIX={dirname}")

    env = dict(os.environ, PREFIX=dirname)
    for item in ["JANET_PATH", "JANET_PREFIX"]:
        if item in env:
            env.pop(item)

    cmd = "make install"
    res = subprocess.run(cmd.split(), env=env, capture_output=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        print(f"Failed to build Janet. RC = {res.returncode}")
        return False
    print(f"  Installed Janet in {dirname}")
    os.chdir(curdir)
    return True


def install_spork(tempdir, dirname):
    curdir = os.getcwd()
    os.chdir(tempdir)
    print(f"Building Spork")

    env = dict(os.environ)
    for item in ["PREFIX", "JANET_PATH", "JANET_PREFIX"]:
        if item in env:
            env.pop(item)

    cmd = f"{dirname}/bin/janet --install ."
    res = subprocess.run(cmd.split(), env=env, capture_output=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        print(f"Failed to install Spork. RC = {res.returncode}")
        return False

    print(f"  Installed Spork in {dirname}")

    os.chdir(curdir)
    return True


def install_jeep(tempdir, dirname):
    curdir = os.getcwd()
    os.chdir(tempdir)
    print(f"Building Jeep")

    env = dict(os.environ)
    for item in ["PREFIX", "JANET_PATH", "JANET_PREFIX"]:
        if item in env:
            env.pop(item)

    cmd = f"{dirname}/bin/janet --install ."
    res = subprocess.run(cmd.split(), env=env, capture_output=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        print(f"Failed to install Jeep. RC = {res.returncode}")
        return False

    print(f"  Installed Jeep in {dirname}")

    os.chdir(curdir)
    return True


def activate_scripts(dirname):
    basename = os.path.basename(dirname)
    inputs = ["activate", "activate.fish"]
    for input in inputs:
        inname = os.path.join("scripts", input)
        outname = os.path.join(os.path.join(dirname, "bin"), input)
        data = open(inname).read()
        with open(outname, "w") as f:
            f.write(data.format(venv_name=basename, venv_dir=dirname))
    return True


def error_and_cleanup(venv_path):
    print("Install failed, cleaning up")
    shutil.rmtree(venv_path)
    return 1


def main(args):
    args = parse_args()
    venv_path = args.dirname

    if os.path.exists(venv_path):
        print(f"Directory {venv_path} already exists.")
        return 1

    with tempfile.TemporaryDirectory() as tempdir:

        janet_dir = get_from_github("janet", "janet-lang", tempdir)
        spork_dir = get_from_github("spork", "janet-lang", tempdir)
        jeep_dir = get_from_github("jeep", "pyrmont", tempdir, branch="master")

        os.makedirs(venv_path)

        if not build_janet(janet_dir, venv_path):
            return error_and_cleanup(venv_path)
        if not install_spork(spork_dir, venv_path):
            return error_and_cleanup(venv_path)
        if not install_jeep(jeep_dir, venv_path):
            return error_and_cleanup(venv_path)

        # install activate/deactivate scripts
        if not activate_scripts(venv_path):
            return error_and_cleanup(venv_path)

        print(finish.format(venv_path=venv_path))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))