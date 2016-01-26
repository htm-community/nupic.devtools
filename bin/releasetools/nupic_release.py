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


  def __init__(self, cliArgs):
    if NAME not in os.environ:
      raise ValueError("You must set a '%s' environment var!" % NAME)
    rootPath = os.environ[NAME] 
    super(NupicRelease, self).__init__(cliArgs, rootPath, name=NAME)
    self.coreReleaseSha = None
    self.coreDevelopmentSha = None


  def release(self, coreReleaseSha, coreDevelopmentSha):
    self.coreReleaseSha = coreReleaseSha
    self.coreDevelopmentSha = coreDevelopmentSha
    super(NupicRelease, self).release()


  def getDoxyFilePath(self):
    return DOXY_FILE
  

  def updateFiles(self, gitlog):
    super(NupicRelease, self).updateFiles(gitlog)
    readmePath = self.getReadmePath()
    
    self.debug("\nUpdating nupic.bindings version number in README.md...")
    required_bindings_version = None
    current_bindings_version = None
    with open(REQUIREMENTS_FILE, "r") as f:
      for line in f.readlines():
        if line.startswith("nupic.bindings"):
          required_bindings_version = line.split("==")[-1].strip()
    if required_bindings_version is None:
      raise Exception("Could not identify nupic.bindings version from %s."
                      % REQUIREMENTS_FILE)
    with open(readmePath, "r") as f:
      for line in f.readlines():
        if "nupic.bindings/nupic.bindings-" in line:
          # Find the nupic.bindings version number to replace
          current_bindings_version = line.split("/")[-1].split("-")[1].strip()
    if required_bindings_version != current_bindings_version:
      self.debug("Updating nupic.bindings version from %s to %s" \
            % (current_bindings_version, required_bindings_version))
      self.replaceInFile(
        current_bindings_version, required_bindings_version, readmePath
      )

    self.debug("\nUpdating .nupic_modules to use last release SHA...")
    shaToReplace = None
    with open(NUPIC_MODULES, "r") as f:
      for line in f.readlines():
        if line.startswith("NUPIC_CORE_COMMITISH"):
          shaToReplace = line.split("=").pop().strip()
    
    self.debug("Replacing %s with %s in %s..." % (shaToReplace, self.coreReleaseSha, NUPIC_MODULES))
    self.replaceInFile(shaToReplace, self.coreReleaseSha, NUPIC_MODULES)


  def createDevelopmentVersion(self):
    self.debug("\nUpdating .nupic_modules to use last development SHA...")
    self.debug("Replacing %s with %s in %s..." % (self.coreReleaseSha, self.coreDevelopmentSha, NUPIC_MODULES))
    self.replaceInFile(self.coreReleaseSha, self.coreDevelopmentSha, NUPIC_MODULES)
    super(NupicRelease, self).createDevelopmentVersion()
