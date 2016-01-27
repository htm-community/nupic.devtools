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
- `export NUPIC_CORE=<path-to-nupic.core-checkout>`
- `pip install libsaas` (For GitHub API calls to publish release)

## Usage

### Release NuPIC Core

Before releasing NuPIC, you should release NuPIC Core. This process will return the NuPIC Core release SHA and HEAD SHA you'll use when releasing NuPIC in a later step. This is necessary to keep the source code synced between the projects at every step.

    > <path/to/>release_nupic_core [options]

This will print the NuPIC Core release SHA and HEAD SHA to the console output. Make a note of these SHA values, because you'll be using them when releasing NuPIC below.

To release NuPIC:

    > <path/to/>release_nupic [options]

To release NuPIC Core:

    > cd $NUPIC_CORE

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

The `release_nupic` script has additionaly options to specify the release and HEAD SHAs for NuPIC Core. This is to ensure that every commit has the right NuPIC Core dependency defined in NuPIC's `.nupic_modules` file.

```

```