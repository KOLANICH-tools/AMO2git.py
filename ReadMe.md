AMO2Git.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
==========
~~[wheel (GitLab)](https://gitlab.com/KOLANICH-libs/AMO2Git.py/-/jobs/artifacts/master/raw/dist/AMO2Git-0.CI-py3-none-any.whl?job=build)~~
~~[wheel (GHA via `nightly.link`)](https://nightly.link/KOLANICH-libs/AMO2Git.py/workflows/CI/master/AMO2Git-0.CI-py3-none-any.whl)~~
~~![GitLab Build Status](https://gitlab.com/KOLANICH-libs/AMO2Git.py/badges/master/pipeline.svg)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH-libs/AMO2Git.py/badges/master/coverage.svg)~~
~~[![GitHub Actions](https://github.com/KOLANICH-libs/AMO2Git.py/workflows/CI/badge.svg)](https://github.com/KOLANICH-libs/AMO2Git.py/actions/)~~
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH-libs/AMO2Git.py.svg)](https://libraries.io/github/KOLANICH-libs/AMO2Git.py)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://codeberg.org/KOLANICH-tools/antiflash.py)

This tool converts a release history on AMO into a git repo history. Useful when the addon developer is uncooperative.

Prerequisites
-------------

1. Install `aria2c`. Windows version can be downloaded [here](https://github.com/aria2/aria2/releases).
2. [Install `git`](https://git-scm.com/download) .
3. [Install `git-lfs`](https://github.com/git-lfs/git-lfs/releases). On Windows git-lfs is shipped with modern versions of [Git for Windows](https://gitforwindows.org/).
4. Install [```Python 3```](https://www.python.org/downloads/). For Windows I recommend [Anaconda](https://www.anaconda.com/download/). [```Python 2``` is dead, stop raping its corpse.](https://python3statement.org/) Use ```2to3``` with manual postprocessing to migrate incompatible code to ```3```. It shouldn't take so much time.
5. Install this tool and its dependencies:
  * [```plumbum```](https://github.com/tomerfiliba/plumbum) [![PyPi Status](https://img.shields.io/pypi/v/plumbum.svg)](https://pypi.python.org/pypi/plumbum) [![TravisCI Build Status](https://travis-ci.org/tomerfiliba/plumbum.svg?branch=master)](https://travis-ci.org/tomerfiliba/plumbum) ![License](https://img.shields.io/github/license/tomerfiliba/plumbum.svg) - for command line interface 

  * [```tqdm```](https://github.com/tqdm/tqdm) [![PyPi Status](https://img.shields.io/pypi/v/tqdm.svg)](https://pypi.python.org/pypi/plumbum) [![TravisCI Build Status](https://travis-ci.org/tqdm/tqdm.svg?branch=master)](https://travis-ci.org/tqdm/tqdm) ![License](https://img.shields.io/github/license/tqdm/tqdm.svg) - for progressbars

  * [```gitpython```](https://github.com/gitpython-developers/GitPython) [![PyPi Status](https://img.shields.io/pypi/v/gitpython.svg)](https://pypi.python.org/pypi/gitpython) [![TravisCI Build Status](https://travis-ci.org/gitpython-developers/GitPython.svg?branch=master)](https://travis-ci.org/gitpython-developers/GitPython) ![License](https://img.shields.io/github/license/gitpython-developers/GitPython.svg) - for operations with git

  * [```requests```](https://github.com/requests/requests) [![PyPi Status](https://img.shields.io/pypi/v/requests.svg)](https://pypi.python.org/pypi/requests) [![TravisCI Build Status](https://travis-ci.org/requests/requests.svg?branch=master)](https://travis-ci.org/requests/requests) ![License](https://img.shields.io/github/license/requests/requests.svg) - for interacting to AMO RESTful API.

Usage
-----

6. Obtain an addon `id`, [`slug`](https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#detail) or guid. Or you can just pass an URI, the program will parse the `slug` from it itself.
7. 
  * On Windows:
    1. `AMO2git retreive <addon slug or URI> > ./retrieve.bat`
    2. `type ./retrieve.bat` and examine the shell script.
    3. `./retrieve.bat`

  * On Linux:
    1. `AMO2git retreive <addon slug or URI> > ./retrieve.sh`
    2. `less ./retrieve.sh` and examine the shell script.
    3. `chmod +x ./retrieve.sh`
    4. `./retrieve.sh`

8. The files will be downloaded to the subdir of the current working directory.
9. `AMO2git convert <addon slug or URI>`
The tool will create a subdir with the repo. [WebExtension](https://developer.mozilla.org/en-US/Add-ons/WebExtensions), [restartless (`bootstrap.js`)](https://developer.mozilla.org/en-US/docs/Archive/Add-ons/Bootstrapped_extensions) and [xul](https://developer.mozilla.org/en-US/docs/Archive/Add-ons/Overlay_Extensions) versions of the addon will be in the corresponding branches. Versions will be marked with tags.
