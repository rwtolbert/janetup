
# janetup

Simple Python script to download, build and
install a Janet install along with Spork and Jeep.

## Prereqs - macOS and Linux

Python3 and gcc/xcode compiler installed.

## Prereqs - Windows
 
Python3, MSVC compiler

## Installation

Clone this repo and run `janetup.py <dirname>` to create
everything in a new directory including scripts to activate 
and deactivate this version in you shell.

Once the script has completed, activate this new environment 
with one of the provided scripts:

### (Bash/ZSH) 

run `. <dirname>/bin/activate` to enter the new environment, then `deactivate` to exit.

### (Fish)

run `source <dirname>/bin/activate.fish` to enter the new environment, then `deactivate` to exit.

### (Powershell)

run `. <dirname>/bin/activate.ps1` to enter the new environment, then `deactivate` to exit.

### To create a new Janet in `janet-dev` on macOS/Linux:

```shell
$ python janetup.py /home/user/jenvs/janet-dev
$ source /home/user/jenvs/janet-dev/bin/activate
$ jeep list
Installed bundles:
   jeep (DEVEL)
   spork

System:
   version: 1.39.1-local
   platform: macos/aarch64/clang
   syspath: /home/user/jenvs/janet-dev/lib/janet

Environment:
   JANET_PATH: <undefined>

Listing completed.
```

### On Windows, in a VS2022 Powershell session:

Note: Jeep is not installed on Windows for now.

```shell
$ python3 .\janetup.py c:\Users\user\test2
$ source c:\Users\user\test2\bin\activate.ps1
$ janet-pm show-config
build dir:  _build
build type: release
curl:       curl
git:        git
offline:    false
pkg list:   https://github.com/janet-lang/pkgs.git
prefix:     C:\Users\user\test2
syspath:    C:\Users\user\test2\Library
tar:        tar
toolchain:  msvc
verbose:    false
workers:    32
```
