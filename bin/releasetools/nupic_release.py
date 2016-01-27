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

from . import Release


NAME = "NUPIC"
# Files that will be modified.
REQUIREMENTS_FILE = "external/common/requirements.txt"
DOXY_FILE = "docs/Doxyfile"
NUPIC_MODULES = ".nupic_modules"


class NupicRelease(Release):


  def __init__(self):
    if NAME not in os.environ:
      raise ValueError("You must set a '%s' environment var!" % NAME)
    rootPath = os.environ[NAME] 
    super(NupicRelease, self).__init__(rootPath, name=NAME)
    parser = self.getParser()
    parser.add_option(
      "-l",
      "--core-release-version",
      default=None,
      dest="coreVersion",
      help="The NuPIC Core version number this release should be associated "
           "with.")
    parser.add_option(
      "-c",
      "--core-release-sha",
      default=None,
      dest="coreReleaseSha",
      help="The NuPIC Core release SHA that this release should be associated "
           "with.")
    parser.add_option(
      "-a",
      "--core-head-sha",
      default=None,
      dest="coreHeadSha",
      help="The NuPIC Core HEAD SHA that continuing development should be "
           "associated with.")
    
    self.coreVersion = None
    self.coreReleaseSha = None
    self.coreHeadSha = None


  def initialize(self, cliArgs):
    parser = self.getParser()
    options, args = parser.parse_args(cliArgs)
  
    if not options.coreVersion:
      parser.error("You must provide a NuPIC Core version number to associate "
                   "this release with. Run with -h for all options.")
    if not options.coreReleaseSha:
      parser.error("You must provide a NuPIC Core release SHA to associate this "
                   "release with. Run with -h for all options.")
    if not options.coreHeadSha:
      parser.error("You must provide a NuPIC Core HEAD SHA to associate this "
                   "continuing NuPIC work. Run with -h for all options.")    
    super(NupicRelease, self).initialize(cliArgs)


  def release(self):
    # Stashing values from custom options defined in initialize() for use later
    # during custom file updates.
    self.coreVersion = self.options.coreVersion
    self.coreReleaseSha = self.options.coreReleaseSha
    self.coreHeadSha = self.options.coreHeadSha
    super(NupicRelease, self).release()


  def getDoxyFilePath(self):
    return DOXY_FILE
  

  def _updateFilesForRelease(self, gitlog):
    super(NupicRelease, self)._updateFilesForRelease(gitlog)
    # Custom file updates for NuPIC.
    self._updateRequirementsTxtForRelease()
    self._updateReadmeForRelease()
    self._updateNupicModulesForRelease()


  def _updateFilesForNextDevelopmentVersion(self):
    super(NupicRelease, self)._updateFilesForNextDevelopmentVersion()
    self._debug("\tUpdating .nupic_modules to use last development SHA...")
    self._replaceInFile(self.coreReleaseSha, self.coreHeadSha, NUPIC_MODULES)
    self._debug("\tUpdating requirements.txt to use latest dev version of nupic.bindings...")
    self._replaceInFile(self.coreVersion, self._getNextReleaseVersion(self.coreVersion), REQUIREMENTS_FILE)


  def _updateNupicModulesForRelease(self):
    self._debug("\tUpdating .nupic_modules to use last release SHA...")
    shaToReplace = None
    with open(NUPIC_MODULES, "r") as f:
      for line in f.readlines():
        if line.startswith("NUPIC_CORE_COMMITISH"):
          shaToReplace = line.split("=").pop().strip()
    self._replaceInFile(shaToReplace, "'%s'" % self.coreReleaseSha, NUPIC_MODULES)


  def _updateRequirementsTxtForRelease(self):
    self._debug("\tUpdating nupic.bindings version number in requirements.txt...")
    oldLine = None
    newLine = "nupic.bindings==%s" % self.coreVersion
    with open(REQUIREMENTS_FILE, "r") as f:
      for line in f.readlines():
        if line.startswith("nupic.bindings"):
          oldLine = line.strip()
    self._replaceInFile(oldLine, newLine, REQUIREMENTS_FILE)


  def _updateReadmeForRelease(self):
    self._debug("\tUpdating nupic.bindings version number in README.md...")
    readmePath = self.getReadmePath()
    coreReleaseVersion = None
    coreCurrentVersion = None
    with open(REQUIREMENTS_FILE, "r") as f:
      for line in f.readlines():
        if line.startswith("nupic.bindings"):
          coreReleaseVersion = line.split("==")[-1].strip()
    if coreReleaseVersion is None:
      raise Exception("Could not identify nupic.bindings version from %s."
                      % REQUIREMENTS_FILE)
    with open(readmePath, "r") as f:
      for line in f.readlines():
        if "nupic.bindings/nupic.bindings-" in line:
          # Find the nupic.bindings version number to replace
          coreCurrentVersion = line.split("/")[-1].split("-")[1].strip()
    if coreReleaseVersion != coreCurrentVersion:
      self._debug("\tUpdating nupic.bindings version from %s to %s" \
                  % (coreCurrentVersion, coreReleaseVersion))
      self._replaceInFile(
        coreCurrentVersion, coreReleaseVersion, readmePath
      )
