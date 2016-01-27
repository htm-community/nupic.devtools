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

This will print the NuPIC Core release SHA and HEAD SHA to the console output. Make a note of these SHA values, because you'll be using them when releasing NuPIC below. The output looks like this:

```
NuPIC Core Released: 0.3.2
NuPIC Core Release SHA: 9f7c868cca976265ae3900d27a77c1a0111ad928
NuPIC Core HEAD SHA: 9697e262a4129816cd52427573dd8ef531d56d8f

To release NuPIC, wait for NuPIC Core release deployment to succeed
and use the SHAs above:

    release_nupic --core-release-version=0.3.2 --core-release-sha=9f7c868cca976265ae3900d27a77c1a0111ad928 --core-head-sha=9697e262a4129816cd52427573dd8ef531d56d8f
```

To release NuPIC:

    > <path/to/>release_nupic [options]

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

The `release_nupic` script has additional options to specify the nupic.bindings version, release SHA, and HEAD SHA for NuPIC Core. This is to ensure that every commit has the right NuPIC Core dependency defined in NuPIC's `.nupic_modules` file.

```
  -l COREVERSION, --core-release-version=COREVERSION
                        The NuPIC Core version number this release should be
                        associated with.
  -c CORERELEASESHA, --core-release-sha=CORERELEASESHA
                        The NuPIC Core release SHA that this release should be
                        associated with.
  -a COREHEADSHA, --core-head-sha=COREHEADSHA
                        The NuPIC Core HEAD SHA that continuing development
                        should be associated with.
```