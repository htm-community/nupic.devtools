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

from releasetools import Release

# Files that will be modified.
REQUIREMENTS_FILE = "external/common/requirements.txt"
DOXY_FILE = "docs/Doxyfile"


class NupicRelease(Release):


  def getDoxyFilePath(self):
    return DOXY_FILE
  

  def updateFiles(self, gitlog):
    super(NupicRelease, self).updateFiles(gitlog)
    readmePath = self.getReadmePath()
    print "\nUpdating nupic.bindings version number in README.md..."
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
      print "Updating nupic.bindings version from %s to %s" \
            % (current_bindings_version, required_bindings_version)
      self.replaceInFile(
        current_bindings_version, required_bindings_version, readmePath
      )
