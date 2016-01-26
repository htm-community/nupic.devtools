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
    help="After this release has completed, what will the next release version"
         "be (if not supplied, it will rollover to bugfix release. You won't"
         "need to use this option unless you need to the next release to break"
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


def getNextReleaseVersion(thisRelease=None):
  if thisRelease:
    last_version = thisRelease
  else:
    with open(VERSION_FILE, "r") as f:
      last_version = f.read().replace('\n', '')
  if last_version[-5:] == DEV_SUFFIX:
    last_version = last_version[0:(0-len(DEV_SUFFIX))]
  dev_split = [int(i) for i in last_version.split('.')]
  dev_split[-1] += 1
  next_version = ".".join([str(i) for i in dev_split])
  return "%s%s" % (next_version, DEV_SUFFIX)


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


  def __init__(self, cliArgs, repoRootPath):
    parser = createOptionsParser()
    (options, args) = parser.parse_args(cliArgs)
    self.options = options
    self.args = args
    self.repoRootPath = repoRootPath
    self.verbose = None
    self.remote = None
    self.releaseType = None
    self.confirm = None
    self.nextRelease = None
    self.ghToken = None
    self.devVersion = None
    self.previousVersion = None
    self.releaseVersion = None


  def debug(self, msg):
    if self.verbose:
      print msg


  def getReadmePath(self):
    return README_FILE


  def getDoxyFilePath(self):
    return DOXY_FILE


  def replaceInFile(self, from_value, to_value, file_path):
    with open(file_path, "r") as f:
      contents = f.read()
    with open(file_path, "wb") as f:
      f.write(contents.replace(from_value, to_value))


  def getGitLog(self):
    previousVersion = self.previousVersion
    gitCommand = "git log %s..HEAD --oneline" % previousVersion
    self.debug(gitCommand)
    # These are all the commit messages since the last release.
    gitlog = subprocess.check_output(gitCommand, shell=True).strip().split("\n")
    # Remove the last log line, because it will just be a commit bumping the
    # version to X.Y.Z.dev0.
    del gitlog[-1]
    return gitlog


  def commitRelease(self):
    print "\nCommitting release..."
    git_command = "git commit -am \"Release %s.\" --no-verify" % self.releaseVersion
    self.debug(git_command)
    subprocess.call(git_command, shell=True)


  def releaseTagExists(self):
    tag = self.releaseVersion
    gitCommand = "git tag"
    self.debug(gitCommand)
    existingTags = subprocess.check_output(gitCommand, shell=True).strip().split("\n")
    return tag in existingTags


  def tagRelease(self):
    releaseVersion = self.releaseVersion
    print "\nTagging release..."
    if self.releaseTagExists():
      delete_tag = queryYesNo(
        "Tag %s already exists! Delete it?" % releaseVersion
      )
      if delete_tag:
        git_command = "git tag -d %s" % releaseVersion
        self.debug(git_command)
        subprocess.call(git_command, shell=True)
      else:
        die("A tag for release %s already exists." % releaseVersion)
    git_command = "git tag -a %s -m \"Release %s\"" \
                  % (releaseVersion, releaseVersion)
    self.debug(git_command)
    subprocess.call(git_command, shell=True)


  def repoNeedsUpdate(self):
    debug = self.debug
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


  def pushRelease(self):
    remote = self.remote
    print "\nPushing to %s..." % remote
    git_command = "git push %s master" % remote
    self.debug(git_command)
    subprocess.call(git_command, shell=True)
    git_command = "git push %s %s" % (remote, self.releaseVersion)
    self.debug(git_command)
    subprocess.call(git_command, shell=True)


  def confirmUserHasPushAccess(self):
    remote = self.remote
    self.debug("Checking if user has push access to %s..." % remote)
    gitCommand = "git push --dry-run %s master" % remote
    self.debug(gitCommand)
    status = subprocess.call(gitCommand, shell=True)
    # User only has push access if exit status of the push call was 0.
    if not status == 0:
        die("You must have push access to remote \"%s\" to create a release." % remote)


  def updateChangelog(self, gitlog, release_version):
    # Changelog needs a little more care.
    self.debug("\tUpdating CHANGELOG.md...")
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


  def updateFiles(self, gitlog):
    releaseVersion = self.releaseVersion
    print "\nUpdating files..."
    # In the README, we want to replace the last release version with the next
    # release version.
    self.debug("\tUpdating README.md...")
    self.replaceInFile(self.previousVersion, releaseVersion, self.getReadmePath())
    # These files can be updated with a simple find/replace:
    for target_file in [VERSION_FILE, self.getDoxyFilePath()]:
      self.debug("\tUpdating %s..." % target_file)
      self.replaceInFile(self.devVersion, releaseVersion, target_file)
    
    self.updateChangelog(gitlog, releaseVersion)


  def createDevelopmentVersion(self):
    lastVersion = self.releaseVersion
    nextRelease = self.nextRelease
    remote = self.remote
    print "\nUpdating version from %s to %s." % (lastVersion, nextRelease)
  
    print "\nUpdating files..."
    self.debug("\tUpdating VERSION...")
    self.replaceInFile(lastVersion, nextRelease, VERSION_FILE)
  
    self.debug("\tUpdating Doxyfile...")
    self.replaceInFile(lastVersion, nextRelease, self.getDoxyFilePath())
  
    print "\nCommitting dev version..."
    git_command = "git commit -am \"Continuing work on %s.\" --no-verify" \
                  % nextRelease
    self.debug(git_command)
    subprocess.call(git_command, shell=True)
  
    if not self.options.dryRun:
      print "\nPushing %s..." % remote
      git_command = "git push %s master" % remote
      subprocess.call(git_command, shell=True)


  def createGithubRelease(self, tag, changes):
    print "\nCreating Release %s in GitHub..." % tag
    gh = github.GitHub(self.ghToken)
    gh_repo = gh.repo("numenta", "nupic")
    release = gh_repo.releases().create({
      "name": tag,
      "tag_name": tag,
      "body": changes
    })
    return release["html_url"]


  def createRelease(self):
    dryRun = self.options.dryRun
    gitlog = self.getGitLog()
  
    if len(gitlog) == 0:
      die("Release contains no changes. Bailing out!")
  
    print "This release contains %i commit(s)." % len(gitlog)
  
    # Strip the SHAs off the beginnings of the commit messages.
    gitlog = [" ".join(line.split(" ")[1:]) for line in gitlog]
  
    self.updateFiles(gitlog)
    self.commitRelease()
    self.tagRelease()
  
    if not dryRun:
      self.pushRelease()


  #### PUBLIC ####


  def check(self):
    options = self.options
    args = self.args

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
  
    self.confirmUserHasPushAccess()


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
        nextRelease = getNextReleaseVersion(releaseVersion)
      elif nextRelease[(0 - len(DEV_SUFFIX)):] != DEV_SUFFIX:
        nextRelease += DEV_SUFFIX
  
      self.nextRelease = nextRelease
  
      print "\n ***************************************"
      print   " * Executing %s release to %s" % (releaseType, releaseVersion)
      print   " ***************************************\n"
      print "  > Updating version from %s to %s" % (self.devVersion, releaseVersion)
      print "  > Previous release was %s" % previousVersion
      print "  > Next development version will be %s" % nextRelease
  
      if self.confirm:
        proceed = queryYesNo(
          "\n\t** WARNING **: You're about to release NuPIC %s (%s).\n"
          "\tThis is a big deal. Are you sure you know what you're doing?"
          % (releaseVersion, releaseType)
        )
        if not proceed:
          die(
            "\nRight. Better safe than sorry. "
            "Email hackers@lists.numenta.org to discuss NuPIC releases.\n"
          )
  
      if self.repoNeedsUpdate():
        die("Your local repo is not up to date with upstream/master, please sync!")
  
      self.createRelease()

      self.createDevelopmentVersion()
  
      if self.options.dryRun:
        print "\n%s was committed and tagged locally but not pushed to %s." \
              % (self.releaseVersion, self.remote)
        print "To reset your local repository to the state it was in before this " \
              "process:"
        print "\tgit reset --hard upstream/master"
        print "\tgit tag -d %s" % self.releaseVersion
      else:
        try:
          release_url = self.createGithubRelease(
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