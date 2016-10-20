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
REQUIREMENTS_FILE = "requirements.txt"
DOXY_FILE = "docs/Doxyfile"
NUPIC_MODULES = ".nupic_modules"


class NupicRelease(Release):


  def __init__(self):
    if NAME not in os.environ:
      raise ValueError("You must set a '%s' environment var!" % NAME)
    rootPath = os.environ[NAME]
    super(NupicRelease, self).__init__(rootPath, name=NAME)


  def getDoxyFilePath(self):
    return DOXY_FILE


  def getAdditionalUserMessage(self):
    return [
      "Requires nupic.bindings %s" % self.getNupicBindingsVersion()
    ]


  def getNupicBindingsVersion(self):
    with open(REQUIREMENTS_FILE, "r") as f:
      for line in f.readlines():
        if line.startswith("nupic.bindings"):
          return line.split("=").pop()


  def getGithubRepo(self):
    return "nupic"
