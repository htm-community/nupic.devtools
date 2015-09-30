# NuPIC Developer Tools

There are two tools here. If you want them add the `bin` folder to your `PATH`:

- [NuPIC build scripts](#nupic-build-scripts)
- [release script](#release-script)

# NuPIC build scripts

These scripts are used to build NuPIC and NuPIC Core from source code cloned into local repositories. Once added to your `PATH`, they may be executed from anywhere in your filesystem. 

> **NOTE**: The help strings below denote paths that will be different on each system, depending on the checkout locations of `NUPIC` and `NUPIC_CORE`. 

## Requirements

- `export NUPIC=<nupic-repo>`
- `export NUPIC_CORE=<nupic-core-repo>`

## Usage

### Installing NuPIC Core

`> install_nupic_core -h`

```
Installs nupic.core from /Users/mtaylor/nta/nupic.core directory. By default, this
installs into /Users/mtaylor/nta/nupic.core/build/release, but can be overridden with the
-r or -s options (see below).

Usage:
> install_nupic_core [options]

Options:
 -c Clean build, removes old build artifacts.
 -v Verbose console output.
 -s build into system location (if specified, -r is ignored)
 -r <release-dir> outputs release to specified directory instead of
    /Users/mtaylor/nta/nupic.core/build/release (default)

Examples:
An installation to default location at /Users/mtaylor/nta/nupic.core/build/release:
    > install_nupic_core
A clean verbose installation to system location:
    > install_nupic_core -cvs
A clean installation to specified location (/tmp):
    > install_nupic_core -c -r /tmp
```

### Installing NuPIC

`> install_nupic -h`

```
Installs NuPIC from /Users/mtaylor/nta/nupic directory. If nupic.core release directory
is not specified with -u or -r options (see below), the nupic.core
binary package is downloaded.

Usage:
> install_nupic [options]

Options:
 -c Clean build, removes old build artifacts.
 -v Verbose console output.
 -u Runs python setup.py install with the --user option.
 -n Builds using nupic.core release at /Users/mtaylor/nta/nupic.core/build/release
 -r <release-dir> Builds using nupic.core release at specified
    directory instead of /Users/mtaylor/nta/nupic.core/build/release.

Examples:
An installation using downloaded nupic.core binary release:
    > install_nupic
A clean verbose installation using nupic.core at
/Users/mtaylor/nta/nupic.core/build/release:
    > install_nupic -cvn
A clean installation using nupic.core at specified location (/tmp):
    > install_nupic -cv -r /tmp
```

### Install All

`> install_nupic_all -h` 

```
Installs NuPIC and nupic.core from their respective source directories.

Usage:
> install_nupic_all [options]

Options:
 -c Clean build, removes old build artifacts.
 -v Verbose console output.
 -u Runs python setup.py install with the --user option.
```

Calls the previous two scripts, ensuring the `nupic.core` release binaries are used for the `nupic` build. 

# Release script

Pushes a new NuPIC release using git tags and the GitHub API. Users must have push access and a GitHub access token.

## Requirements:
- git
- Push access to target git repository
- `export GH_ACCESS_TOKEN=<token>` ([GitHub access token](https://github.com/blog/1509-personal-api-tokens))
  - > Be sure you choose "admin" permissions!
- `export NUPIC=<path-to-nupic-checkout>`
- `pip install libsaas` (For GitHub API calls to publish release)

## Usage

    > cd $NUPIC
    > <path/to/>release_nupic [options]

##Options
```
  -h, --help            show this help message and exit
  -v, --verbose         Print debugging statements.
  -d, --dry-run         Prevents pushing to remote branch.
  -y, --yes             Prevents command line confirmation for the release.
                        Hopefully you know what you're doing.
  -r REMOTE, --remote=REMOTE
                        Which remote location to push to (default 'upstream').
  -s RELEASE_TYPE, --semantic-release-type=RELEASE_TYPE
                        Type of semantic release to execute. Must be either
                        "bugfix", "minor", or "major" (default "bugfix").
```
