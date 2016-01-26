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
import subprocess

from releasetools import Release


class NupicCoreRelease(Release):


  def commitRelease(self):
    super(NupicCoreRelease, self).commitRelease()
    self.releaseSha = subprocess.check_output(
      "git rev-parse HEAD", shell=True
    ).strip()
  
  
  def release(self):
    super(NupicCoreRelease, self).release()
    return self.getReleaseSha()


  def getReleaseSha(self):
    return self.releaseSha
