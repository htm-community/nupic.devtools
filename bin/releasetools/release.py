# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2015-2016, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# ----------------------------------------------------------------------
import os
import sys
import subprocess

from optparse import OptionParser

from libsaas.services import github
from libsaas.http import HTTPError

# Files that will be modified.
README_FILE = "README.md"
VERSION_FILE = "VERSION"
CHANGELOG_FILE = "CHANGELOG.md"
DOXY_FILE = "Doxyfile"

BUGFIX_RELEASE = "bugfix"
MINOR_RELEASE = "minor"
MAJOR_RELEASE = "major"

DEFAULT_releaseType = BUGFIX_RELEASE
DEFAULT_REMOTE = "upstream"

# Used for creating the next version after the release. After 1.2.3 comes
# 1.2.3.dev0. Named this way because distutils complains if you use "-dev".
# You know you hate it when distutils complains.
DEV_SUFFIX = ".dev0"


def createOptionsParser():
  # Options parsing.
  parser = OptionParser(
    usage="%prog [options]\n\n"
          """
  Pushes a new NuPIC release using git tags and the GitHub API. Users must have push access and a GitHub access token.

  ## Requirements:
  - git
  - [GitHub access token](https://github.com/blog/1509-personal-api-tokens)
    - `export GH_ACCESS_TOKEN=<token>`
  - `export NUPIC=<path-to-nupic-checkout>`
  - Push access to target git repository
  - `pip install libsaas`

  ## Usage

  > ./release_nupic [options]

  It's assumed you're releasing NuPIC, so the value of the `NUPIC` environment variable will be used for the repository location.
          """
  )

  parser.add_option(
    "-v",
    "--verbose",
    action="store_true",
    default=False,
    dest="verbose",
    help="Print debugging statements.")
  parser.add_option(
    "-d",
    "--dry-run",
    action="store_true",
    default=False,
    dest="dryRun",
    help="Prevents pushing to remote branch.")
  parser.add_option(
    "-y",
    "--yes",
    action="store_true",
    default=False,
    dest="auto_confirm",
    help="Prevents command line confirmation for the release. "
         "Hopefully you know what you're doing.")
  parser.add_option(
    "-r",
    "--remote",
    default=DEFAULT_REMOTE,
    dest="remote",
    help="Which remote location to push to (default 'upstream').")
  parser.add_option(
    "-n",
    "--next-release",
    default=None,
    dest="nextRelease",
    help="After this release has completed, what will the next release version "
         "be (if not supplied, it will rollover to bugfix release. You won't "
         "need to use this option unless you need to the next release to break "
         "semantic versioning.")
  parser.add_option(
    "-s",
    "--semantic-release-type",
    default=DEFAULT_releaseType,
    dest="releaseType",
    help="Type of semantic release to execute. Must be either \"%s\", "
         "\"%s\", or \"%s\" (default \"%s\")."
         % (BUGFIX_RELEASE, MINOR_RELEASE, MAJOR_RELEASE, BUGFIX_RELEASE))

  return parser


def queryYesNo(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def die(msg):
  print msg
  exit(-1)


def findVersions(devVersion, releaseType):
  # Turns "X.Y.Z.dev0 into "X.Y.Z".
  expectedNextVersion = ".".join(devVersion.split(".")[:-1])
  releaseSplit = [int(i) for i in expectedNextVersion.split('.')]

  releaseSplit[-1] -= 1
  previousVersion = ".".join([str(i) for i in releaseSplit])

  if releaseType == BUGFIX_RELEASE:
    releaseVersion = expectedNextVersion
  elif releaseType == MINOR_RELEASE:
    # Bump minor number.
    releaseSplit[-2] += 1
    # Rollover bugfix number.
    releaseSplit[-1] = 0
    releaseVersion = ".".join([str(i) for i in releaseSplit])
  else:
    # Bump major number.
    releaseSplit[0] += 1
    # Rollover minor and bugfix numbers.
    releaseSplit[1] = 0
    releaseSplit[2] = 0
    releaseVersion = ".".join([str(i) for i in releaseSplit])

  return previousVersion, releaseVersion


def pause(message):
  sys.stdout.write(message + " To resume this script, press enter.")
  raw_input()


def getReleaseNotes(release_number):
  release_notes = []
  in_release = False
  with open(CHANGELOG_FILE, "r") as f:
    for line in f.readlines():
      if in_release:
        if line.startswith("##"):
          break
        release_notes.append(line)
      if line == "## %s\n" % release_number:
        in_release = True
  return "".join(release_notes)



class Release(object):


  def __init__(self, repoRootPath, name="Unknown"):
    self.repoRootPath = repoRootPath
    self.options = None
    self.args = None
    self.name = name
    self.releaseSha = None
    self.devSha = None
    self.verbose = None
    self.remote = None
    self.releaseType = None
    self.confirm = None
    self.nextRelease = None
    self.ghToken = None
    self.devVersion = None
    self.previousVersion = None
    self.releaseVersion = None
    self.parser = createOptionsParser()


  def _debug(self, msg):
    if self.verbose:
      print msg


  def _replaceInFile(self, fromValue, toValue, filePath):
    if not os.path.isfile(filePath):
      self._debug("\tSkipping %s (does not exist)..." % filePath)
    else:
      self._debug("\tReplacing %s with %s in %s..." % (fromValue, toValue, filePath))
      with open(filePath, "r") as f:
        contents = f.read()
      with open(filePath, "wb") as f:
        f.write(contents.replace(fromValue, toValue))


  def _getNextReleaseVersion(self, thisRelease=None):
    if thisRelease:
      lastVersion = thisRelease
    else:
      with open(VERSION_FILE, "r") as f:
        lastVersion = f.read().replace('\n', '')
    if lastVersion[-5:] == DEV_SUFFIX:
      lastVersion = lastVersion[0:(0-len(DEV_SUFFIX))]
    devSplit = [int(i) for i in lastVersion.split('.')]
    devSplit[-1] += 1
    nextVersion = ".".join([str(i) for i in devSplit])
    return "%s%s" % (nextVersion, DEV_SUFFIX)


  def _getGitLog(self):
    previousVersion = self.previousVersion
    gitCommand = "git log %s..HEAD --oneline" % previousVersion
    self._debug(gitCommand)
    # These are all the commit messages since the last release.
    gitlog = subprocess.check_output(gitCommand, shell=True).strip().split("\n")
    # Remove the last log line, because it will just be a commit bumping the
    # version to X.Y.Z.dev0.
    del gitlog[-1]
    return gitlog


  def _commitRelease(self):
    print "\nCommitting release..."
    gitCommand = "git commit -am \"Release %s.\" --no-verify" % self.releaseVersion
    self._debug(gitCommand)
    subprocess.call(gitCommand, shell=True)
    self.releaseSha = subprocess.check_output(
      "git rev-parse HEAD", shell=True
    ).strip()


  def _releaseTagExists(self):
    tag = self.releaseVersion
    gitCommand = "git tag"
    self._debug(gitCommand)
    existingTags = subprocess.check_output(gitCommand, shell=True).strip().split("\n")
    return tag in existingTags


  def _tagRelease(self):
    releaseVersion = self.releaseVersion
    print "\nTagging release..."
    if self._releaseTagExists():
      delete_tag = queryYesNo(
        "Tag %s already exists! Delete it?" % releaseVersion
      )
      if delete_tag:
        git_command = "git tag -d %s" % releaseVersion
        self._debug(git_command)
        subprocess.call(git_command, shell=True)
      else:
        die("A tag for release %s already exists." % releaseVersion)
    git_command = "git tag -a %s -m \"Release %s\"" \
                  % (releaseVersion, releaseVersion)
    self._debug(git_command)
    subprocess.call(git_command, shell=True)


  def _repoNeedsUpdate(self):
    debug = self._debug
    remote = self.remote
    debug("Checking if local repo needs to be synced with %s..." % remote)

    gitCommand = "git fetch %s" % remote
    debug(gitCommand)
    subprocess.call(gitCommand, shell=True)

    # This gives us a log of all the commits on <remote>/master that aren't on
    # the local checkout's HEAD.
    gitCommand = "git log HEAD..%s/master --oneline" % remote
    debug(gitCommand)
    gitlog = subprocess.check_output(gitCommand, shell=True).strip()

    # If the output is not empty, then the repo needs updating.
    return len(gitlog) > 0


  def _pushRelease(self):
    remote = self.remote
    print "\nPushing to %s..." % remote
    git_command = "git push %s master" % remote
    self._debug(git_command)
    subprocess.call(git_command, shell=True)
    git_command = "git push %s %s" % (remote, self.releaseVersion)
    self._debug(git_command)
    subprocess.call(git_command, shell=True)


  def _confirmUserHasPushAccess(self):
    remote = self.remote
    self._debug("Checking if user has push access to %s %s..." % (self.name, remote))
    gitCommand = "git push --dry-run %s master" % remote
    self._debug(gitCommand)
    status = subprocess.call(gitCommand, shell=True)
    # User only has push access if exit status of the push call was 0.
    if not status == 0:
        die("You must have push access to remote \"%s\" to create a release." % remote)


  def _updateChangelog(self, gitlog, release_version):
    # Changelog needs a little more care.
    self._debug("\n\tUpdating CHANGELOG.md...")
    # This is a bit more complex than a substitution.
    with open(CHANGELOG_FILE, "r") as f:
      changelog_contents = f.readlines()
    new_changelog_contents = []
    for line in changelog_contents:
      # At the top of the changelog, add a line for this release version.
      if line == "# Changelog\n":
        new_changelog_contents.append(line)
        new_changelog_contents.append("\n## %s\n\n" % release_version)
        changelog_count = 0
        # Loop through all the git log messages since the last version.
        for log_line in gitlog:
          # There are some commit messages we can always ignore.
          if not log_line.startswith("Merge pull request") \
                  and not log_line.startswith("Merge branch") \
                  and not log_line.startswith("Updates nupic.core to"):
            # Ask the user doing the release if they want each commit message in the
            # changelog.
            include = "Include this change in the CHANGELOG?\n\t\"%s\"" % log_line
            if queryYesNo(include):
              changelog_count += 1
              new_changelog_contents.append("* %s\n" % log_line)
      else:
        new_changelog_contents.append(line)
    with open(CHANGELOG_FILE, "wb") as f:
      f.writelines(new_changelog_contents)
    manual_changelog_change = queryYesNo(
      "\nDo you want to make any manual changes to the CHANGELOG file before "
      "continuing?"
    )
    if manual_changelog_change:
      pause("Edit the CHANGELOG.md file now and save without committing.")


  def _updateFilesForRelease(self, gitlog):
    releaseVersion = self.releaseVersion
    print "\nUpdating files for release..."
    # In the README, we want to replace the last release version with the next
    # release version.
    self._debug("\tUpdating README.md...")
    self._replaceInFile(self.previousVersion, releaseVersion, self.getReadmePath())
    # These files can be updated with a simple find/replace:
    for target_file in [VERSION_FILE, self.getDoxyFilePath()]:
      self._debug("\tUpdating %s..." % target_file)
      self._replaceInFile(self.devVersion, releaseVersion, target_file)

    self._updateChangelog(gitlog, releaseVersion)


  def _updateFilesForNextDevelopmentVersion(self):
    print "\nUpdating files for next development version..."
    lastVersion = self.releaseVersion
    nextRelease = self.nextRelease
    self._debug("\tUpdating VERSION...")
    self._replaceInFile(lastVersion, nextRelease, VERSION_FILE)
    self._debug("\tUpdating Doxyfile...")
    self._replaceInFile(lastVersion, nextRelease, self.getDoxyFilePath())



  def _createDevelopmentVersion(self):
    nextRelease = self.nextRelease
    remote = self.remote

    self._updateFilesForNextDevelopmentVersion()

    print "\nCommitting dev version..."
    git_command = "git commit -am \"Continuing work on %s.\" --no-verify" \
                  % nextRelease
    self._debug(git_command)
    subprocess.call(git_command, shell=True)
    self.devSha = subprocess.check_output(
      "git rev-parse HEAD", shell=True
    ).strip()

    if not self.options.dryRun:
      print "\nPushing %s..." % remote
      git_command = "git push %s master" % remote
      subprocess.call(git_command, shell=True)


  def _createGithubRelease(self, tag, changes):
    print "\nCreating Release %s in GitHub..." % tag
    gh = github.GitHub(self.ghToken)
    gh_repo = gh.repo(self.getGithubOrg(), self.getGithubRepo())
    release = gh_repo.releases().create({
      "name": tag,
      "tag_name": tag,
      "body": changes
    })
    return release["html_url"]


  def _createRelease(self):
    dryRun = self.options.dryRun
    gitlog = self._getGitLog()

    if len(gitlog) == 0:
      die("Release contains no changes. Bailing out!")

    print "This release contains %i commit(s)." % len(gitlog)

    # Strip the SHAs off the beginnings of the commit messages.
    gitlog = [" ".join(line.split(" ")[1:]) for line in gitlog]

    self._updateFilesForRelease(gitlog)
    self._commitRelease()
    self._tagRelease()

    if not dryRun:
      self._pushRelease()


  #### PUBLIC ####


  def initialize(self, cliArgs):
    (options, args) = self.parser.parse_args(cliArgs)
    self.options = options
    self.args = args


  def getReleaseSha(self):
    return self.releaseSha


  def getDevelopmentSha(self):
    return self.devSha


  def getParser(self):
    return self.parser


  def getReadmePath(self):
    return README_FILE


  def getDoxyFilePath(self):
    return DOXY_FILE


  def getGithubOrg(self):
    return "numenta"


  def getGithubRepo(self):
    pass


  def getAdditionalUserMessage(self):
    """
    This method is meant to be overridden by subclasses to provide more user
    information that will be displayed to the user before the script starts a
    release.
    """
    return []


  def check(self):
    options = self.options
    args = self.args

    cwd = os.getcwd()
    os.chdir(self.repoRootPath)

    try:
      if "GH_ACCESS_TOKEN" not in os.environ:
        die("Set the GH_ACCESS_TOKEN environment variable.")
      self.ghToken = os.environ["GH_ACCESS_TOKEN"]

      self.verbose = options.verbose
      self.confirm = not options.auto_confirm
      self.nextRelease = options.nextRelease
      self.releaseType = options.releaseType

      self.remote = options.remote

      if self.releaseType not in [BUGFIX_RELEASE, MINOR_RELEASE, MAJOR_RELEASE]:
        die("Invalid semantic release type \"%s\"." % self.releaseType)

      # Unpublished feature: first argument can be a path to a repository location.
      # Currently used for testing this script.
      if len(args) > 0:
        self.repoRootPath = os.path.abspath(args[0])

      self._confirmUserHasPushAccess()
    finally:
      os.chdir(cwd)


  def release(self):
    repo = self.repoRootPath
    nextRelease = self.nextRelease
    releaseType = self.releaseType
    cwd = os.getcwd()
    os.chdir(repo)
    try:
      with open(VERSION_FILE, "r") as f:
        self.devVersion = f.read().strip()

      previousVersion, releaseVersion = findVersions(
        self.devVersion, self.releaseType
      )
      self.previousVersion = previousVersion
      self.releaseVersion = releaseVersion

      if nextRelease is None:
        nextRelease = self._getNextReleaseVersion(releaseVersion)
      elif nextRelease[(0 - len(DEV_SUFFIX)):] != DEV_SUFFIX:
        nextRelease += DEV_SUFFIX

      self.nextRelease = nextRelease

      print ""
      print " ***************************************"
      print " * RELEASING: "
      print " *            %s %s (%s)" % (self.name, releaseVersion, releaseType)
      if self.options.dryRun:
        print " *            [DRY RUN]"
      print " ***************************************\n"
      print " (Not what you wanted? Use --help for more options.)\n"
      print "  > Updating version from %s to %s" % (self.devVersion, releaseVersion)
      print "  > Previous release was %s" % previousVersion
      print "  > This release is %s" % releaseVersion
      print "  > Next development version will be %s" % nextRelease

      for line in self.getAdditionalUserMessage():
        print "  > %s" % line

      if self.confirm:
        proceed = queryYesNo(
          "\n\t** WARNING **\n\n"
          "\tYou're about to release %s %s (%s).\n"
          "\tOnly NuPIC Committers are allowed to run this script.\n"
          "\tAre you sure you know what you're doing?"
          % (self.name, releaseVersion, releaseType)
        )
        if not proceed:
          die(
            "\nBetter safe than sorry!\n"
            "\nVisit https://discourse.numenta.org/c/nupic/developers to discuss NuPIC releases.\n"
          )

      if self._repoNeedsUpdate():
        die("Your local repo is not up to date with upstream/master, please sync!")

      self._createRelease()

      self._createDevelopmentVersion()

      if self.options.dryRun:
        print "\n%s %s was committed and tagged locally but not pushed to %s." \
              % (self.name, self.releaseVersion, self.remote)
        print "To reset your local repository to the state it was in before this " \
              "process:"
        print "\tgit reset --hard upstream/master"
        print "\tgit tag -d %s" % self.releaseVersion
      else:
        try:
          release_url = self._createGithubRelease(
            self.releaseVersion, getReleaseNotes(self.releaseVersion)
          )
          print "See %s" % release_url
        except HTTPError as http_error:
          print http_error
          print("Error publishing release information to GitHub! But don't "
                "worry, you can do that manually at github.com.")
        print "\nDone releasing %s." % self.releaseVersion

    finally:
      # Always change back to original directory, even if fatal errors occur.
      os.chdir(cwd)

    return self.releaseVersion
