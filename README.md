# NuPIC Developer Tools

This repository contains developer tools for NuPIC.

## NuPIC / NuPIC Core Release Scripts

Pushes a new release using git tags and the GitHub API. Users must have push access and a GitHub access token.

## Requirements:
- git
- Push access to target git repository
- `export GH_ACCESS_TOKEN=<token>` ([GitHub access token](https://github.com/blog/1509-personal-api-tokens))
  - > Be sure you choose "admin" permissions!
- `export NUPIC=<path-to-nupic-checkout>`
- `pip install libsaas` (For GitHub API calls to publish release)

## Usage

To release NuPIC:

    > cd $NUPIC
    > <path/to/>release_nupic [options]

To release NuPIC Core:

    > cd $NUPIC_CORE
    > <path/to/>release_nupic_core [options]

## Options
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
