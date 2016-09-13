> **WARNING**: While the NuPIC Core release script still works for publishing new `nupic.bindings` to PyPi, the NuPIC release script is now deprecated after the merge of https://github.com/numenta/nupic/pull/3314. The new release process for both `nupic.bindings` and `nupic` will be tied to our new [Bamboo CI instance](https://ci.numenta.com/).

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

Typically, NuPIC will be released immediately after NuPIC Core releases are created **and they have been deployed via CI**. Running the `release_nupic` script will fail if the builds created by running the `release_nupic_core` script have not finished (or failed to complete successfully). For this reason, it is currently impossible to create one script that releases both NuPIC and NuPIC Core in one fell swoop.

### Release NuPIC Core

This process will return the NuPIC Core release version number, the release SHA, and the HEAD SHA for continuing development. You'll use all these values when releasing NuPIC in a later step. This is necessary to keep the source code synced between the projects at every step.

    > bin/release_nupic_core [options]

There is a lot of output to this script, especially if you use `--verbose`, but the last part of the output looks like something this:

```
NuPIC Core Released: 0.3.2
NuPIC Core Release SHA: 9f7c868cca976265ae3900d27a77c1a0111ad928
NuPIC Core HEAD SHA: 9697e262a4129816cd52427573dd8ef531d56d8f

To release NuPIC, wait for NuPIC Core release deployment to succeed
and use the SHAs above:

    release_nupic --core-release-version=0.3.2 --core-release-sha=9f7c868cca976265ae3900d27a77c1a0111ad928 --core-head-sha=9697e262a4129816cd52427573dd8ef531d56d8f
```

As you can see, the exact command options for the next step are included in the output. But if you run this command immediately, the builds created by the script will fail.

> **_NuPIC Core builds created by the release process must pass before moving on to the NuPIC release._**

### Release NuPIC

Once CI builds from the NuPIC Core release have passed, you can be assured that artifacts required for the NuPIC release have been published. 

    > <path/to/>release_nupic --core-release-version=X.Y.Z --core-release-sha=XXXXXXXXXXXXXXXXX --core-head-sha=YYYYYYYYYYYYYYYY [options]

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

The `release_nupic` script has additional options to specify the NuPIC Core version, release SHA, and HEAD SHA for NuPIC Core. This is to ensure that every commit has the right NuPIC Core dependency defined in NuPIC's `.nupic_modules` file.

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
