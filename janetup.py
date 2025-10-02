import argparse
import glob
import json
import os
import re
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

finish_win32 = """
Created new Janet environment at {venv_path}:

(Powershell)
    `. {venv_path}\\bin\\activate.ps1`
    to enter the new environment, then `deactivate` to exit.
"""

# waiting for Windows support
#(PowerShell) run `. {venv_path}/bin/activate.ps1` to enter the new environment, then `deactivate` to exit.
#(CMD)        run `{venv_path}\bin\activate` to enter the new environment, then `deactivate` to exit.

epilog = '''
Where VERSION can be one of several formats:

    release=<release> - choose a specific released version
    branch=<branch> - choose a specific branch, as in `branch=master`
    tag=<tag> - choose a specific tag, as in `tag=v1.38.0`
    commit=<HASH> - choose a specific commit hash, as in `commit=8fd1672`

Default is `release=latest` for Janet, `branch=master` for Spork and Jeep.
'''

def parse_args():
    parser = argparse.ArgumentParser(
        prog='janetup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Install a custom Janet build, in an isolated environment.',
        epilog=epilog)

    parser.add_argument('dirname', help="Directory for new Janet build")

    parser.add_argument('--janet',
                        metavar="VERSION",
                        default="release=latest",
                        help="Janet version to install.")

    parser.add_argument('--spork',
                        metavar="VERSION",
                        default="branch=master",
                        help="Spork version to install.")

    parser.add_argument('--jeep',
                        metavar="VERSION",
                        default="branch=master",
                        help="Jeep version to install.")

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
                if release is None or release == "latest" and len(releases) > 0:
                    tag = releases[0]
                elif release in releases:
                    tag = release
                else:
                    print(f"Could not find the release '{release}' for '{name}'.")
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
        message = f"{name} - commit:{commit}"

    print(f"Downloading {message}")

    try:
        path, msg = urllib.request.urlretrieve(url, file_name)
    except urllib.request.HTTPError:
        #print(f"Could not download {name} @ {url}.")
        return None

    tar = tarfile.open(file_name)
    outdir = os.path.abspath(f"{name}_git")
    tar.extractall(path=outdir, filter='data')
    tar.close()
    os.remove(file_name)

    os.chdir(outdir)
    files = glob.glob(f"{name}*")
    if len(files) == 0:
        #print(f"Could not find {name} @ {url}.")
        return None

    outdir = os.path.abspath(files[0])

    os.chdir(curdir)
    return outdir


def build_janet(tempdir, dirname, git_hash):
    curdir = os.getcwd()
    os.chdir(tempdir)
    print(f"Building Janet, PREFIX={dirname}")

    success = True
    env = dict(os.environ, PREFIX=dirname)
    for item in ["JANET_PATH", "JANET_PREFIX"]:
        if item in env:
            env.pop(item)

    if sys.platform == "win32":
        cmd = f"meson setup build --buildtype release --optimization 2 --prefix {dirname} -Dgit_hash={git_hash}"
        res = subprocess.run(cmd.split(), env=env)
        if res.returncode != 0:
            print("Meson failed.")
            success = False
        else:
            cmd = "ninja -C build"
            res = subprocess.run(cmd.split(), env=env)
            if res.returncode != 0:
                print("Ninja failed.")
                success = False
            else:
                cmd = "ninja -C build install"
                res = subprocess.run(cmd.split(), env=env)
                if res.returncode != 0:
                    print("Ninja install failed.")
                    success = False

        # need to do some fixup for expected Windows file paths
        # this is really a fix that should be put into the Meson build itself
        # when running on Windows.
        if success:
            # janet.h
            C_dir = os.path.join(dirname, "C")
            os.makedirs(C_dir)
            include_dir = os.path.join(os.path.join(dirname, "include/janet"))
            h_files = glob.glob(os.path.join(include_dir, "janet*h"))
            if len(h_files) == 1:
                shutil.copy(os.path.join(include_dir, h_files[0]), os.path.join(C_dir, "janet.h"))
            # janet.lib
            lib_dir = os.path.join(os.path.join(dirname, "lib"))
            lib_files = glob.glob(os.path.join(lib_dir, "*.*"))
            for f in lib_files:
                outname = os.path.basename(f)
                if outname == "libjanet.a":
                    outname = "libjanet.lib"
                dest = os.path.join(C_dir, outname)
                print(f"->> Copying {f} to {dest}")
                shutil.copy(os.path.join(lib_dir, f), dest)

    else:
        cmd = "make install"
        res = subprocess.run(cmd.split(), env=env, capture_output=True)
        if res.returncode != 0:
            print(res.stdout)
            print(res.stderr)
            print(f"Failed to build Janet. RC = {res.returncode}")
            success = False

    if success:
        print(f"  Installed Janet in {dirname}")
    os.chdir(curdir)
    return success


def install_spork(tempdir, dirname):
    curdir = os.getcwd()
    os.chdir(tempdir)
    print(f"Building Spork")

    env = dict(os.environ)
    for item in ["PREFIX", "JANET_PATH", "JANET_PREFIX", "JANET_BINPATH",
                 "JANET_LIBPATH", "JANET_HEADERPATH", "JANET_MANPATH"]:
        if item in env:
            env.pop(item)

    # help janet/cc find the headers and libs
    if sys.platform == "win32":
        env["JANET_PREFIX"] = dirname

    cmd = f"{dirname}/bin/janet --install ."
    res = subprocess.run(cmd.split(), env=env)
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

    # help janet/cc find the headers and libs
    if sys.platform == "win32":
        env["JANET_PREFIX"] = dirname

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
    if sys.platform == "win32":
        inputs = ["activate.ps1"]
    else:
        inputs = ["activate", "activate.fish"]
    for input in inputs:
        inname = os.path.join("scripts", input)
        outname = os.path.join(os.path.join(dirname, "bin"), input)
        data = open(inname).read()
        with open(outname, "w") as f:
            f.write(data.format(venv_name=basename, venv_dir=dirname))
    return True


def validate_version(version):
    parts = version.strip().split("=")
    if len(parts) != 2:
        print(f"Invalid version: {version}")
        return None
    if parts[0] not in ["release", "branch", "tag", "commit"]:
        print(f"Invalid version type: {parts[0]} must be from 'release' or 'branch' or 'tag' or 'commit'")
        return None
    return parts[0], parts[1]


def get_thing(owner, repo, tempdir, version):
    parts = validate_version(version)
    if parts is None:
        return None
    res = None
    if parts[0] == "release":
        res = get_from_github(repo, owner, tempdir, release=parts[1])
    elif parts[0] == "branch":
        res = get_from_github(repo, owner, tempdir, branch=parts[1])
    elif parts[0] == "tag":
        res = get_from_github(repo, owner, tempdir, tag=parts[1])
    elif parts[0] == "commit":
        res = get_from_github(repo, owner, tempdir, commit=parts[1])

    if res is None:
        print(f"Unable to get {repo} @ {parts[0]} = {parts[1]}")
    return res


def error_and_cleanup(venv_path, curdir):
    os.chdir(curdir)
    print("Install failed, cleaning up")
    if os.path.isdir(venv_path):
        shutil.rmtree(venv_path)
    return 1


def main(args):
    args = parse_args()
    venv_path = os.path.abspath(args.dirname)

    if os.path.exists(venv_path):
        print(f"Directory {venv_path} already exists.")
        return 1

    curdir = os.getcwd()
    with tempfile.TemporaryDirectory() as tempdir:
        janet_dir = get_thing("janet-lang", "janet", tempdir, version=args.janet)
        if janet_dir is None:
            return error_and_cleanup(venv_path, curdir)

        # get hash for build
        base_name = os.path.basename(janet_dir)
        parts = base_name.split("-")
        if len(parts) == 2 and len(parts[1]) == 40 and re.match(r"[0-9a-f]", parts[1]):
            git_hash = parts[1][:7]
        else:
            git_hash = "local"

        spork_dir = get_thing( "janet-lang", "spork", tempdir, version=args.spork)
        if spork_dir is None:
            return error_and_cleanup(venv_path, curdir)

        os.makedirs(venv_path)

        if not build_janet(janet_dir, venv_path, git_hash):
            return error_and_cleanup(venv_path, curdir)
        if not install_spork(spork_dir, venv_path):
            return error_and_cleanup(venv_path, curdir)

        if sys.platform == "win32":
            print("skipping Jeep on Windows")
        else:
            jeep_dir = get_thing("pyrmont", "jeep", tempdir, version=args.jeep)
            if jeep_dir is None:
                return error_and_cleanup(venv_path, curdir)
            if not install_jeep(jeep_dir, venv_path):
                return error_and_cleanup(venv_path, curdir)

        # install activate/deactivate scripts
        if not activate_scripts(venv_path):
            return error_and_cleanup(venv_path, curdir)
        os.chdir(curdir)

    if sys.platform == "win32":
        print(finish_win32.format(venv_path=venv_path))
    else:
        print(finish.format(venv_path=venv_path))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))