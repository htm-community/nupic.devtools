# NuPIC Developer Tools

This repository contains developer tools for NuPIC. Currently, this only includes code to create new releases for NuPIC and NuPIC Core.

## NuPIC / NuPIC Core Release Scripts

This code pushes a new release using git tags and the GitHub API. Users must have push access and a GitHub access token. NuPIC should be released soon after the NuPIC Core release.

## Requirements:
- git
- Push access to target git repository
- `export GH_ACCESS_TOKEN=<token>` ([GitHub access token](https://github.com/blog/1509-personal-api-tokens))
  - _Be sure you choose "admin" permissions!_
- `export NUPIC=<path-to-nupic-checkout>`
- `export NUPIC_CORE=<path-to-nupic.core-checkout>`
- `pip install libsaas` (For GitHub API calls to publish release)

## Usage

### Release NuPIC Core

This process will return the NuPIC Core release version number, the release SHA, and the HEAD SHA for continuing development. You'll use all these values when releasing NuPIC in a later step. This is necessary to keep the source code synced between the projects at every step.

    > bin/release_nupic_core [options]

### Release NuPIC

    > bin/release_nupic [options]

## Options

These options work for both `release_nupic` and `release_nupic_core`:

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
