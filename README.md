# NuPIC Developer Tools

I keep scripts I use for NuPIC development here. More details at some point.

## Assumptions

### For installation scripts...

- You have the `NUPIC` environment variable set to the path of your NuPIC checkout.
- You have the `NUPIC_CORE` environment variable set to the path of your `nupic.core` checkout.

### For release script...

- You have `git` installed.
- You have a [GitHub personal access token](https://github.com/blog/1509-personal-api-tokens) set as the `GH_ACCESS_TOKEN` environment variable.
- You are a NuPIC committer (you have push access), required for releasing.

## Installation

### For installation scripts:

Add the `bin` folder to your `PATH`.

### For release script:

    pip install libsaas

## Usage

### Installing NuPIC Core

Call the `install_core` script.

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

Call the `install_nupic` script.

```
Installs NuPIC from /Users/mtaylor/nta/nupic directory. If nupic.core release directory
is not specified with -u or -r options (see below), the nupic.core
binary package is downloaded.

Usage:
> install_nupic [options]

Options:
 -c Clean build, removes old build artifacts.
 -v Verbose console output.
 -u Builds using nupic.core release at /Users/mtaylor/nta/nupic.core/build/release
 -r <release-dir> Builds using nupic.core release at specified
    directory instead of /Users/mtaylor/nta/nupic.core/build/release.

Examples:
An installation using downloaded nupic.core binary release:
    > install_nupic
A clean verbose installation using nupic.core at
/Users/mtaylor/nta/nupic.core/build/release:
    > install_nupic -cvu
A clean installation using nupic.core at specified location (/tmp):
    > install_nupic -cv -r /tmp
```

### Install Both NuPIC and NuPIC Core

Call the `install_nupic_all` script, which calls the previous two scripts with the `-c` options and ensures the `nupic.core` release binaries are used for the `nupic` build. 
