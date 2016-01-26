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
import subprocess

from . import Release


NAME = "NUPIC_CORE"


class NupicCoreRelease(Release):


  def __init__(self, cliArgs):
    if NAME not in os.environ:
      raise ValueError("You must set a '%s' environment var!" % NAME)
    rootPath = os.environ[NAME] 
    super(NupicCoreRelease, self).__init__(cliArgs, rootPath, NAME)


  def release(self):
    super(NupicCoreRelease, self).release()
    return self.getReleaseSha(), self.getDevelopmentSha()
