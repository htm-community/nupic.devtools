#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import sys
import os

from releasetools.nupic_release import NupicRelease
from releasetools.nupic_core_release import NupicCoreRelease

if __name__ == "__main__":

  if "NUPIC" not in os.environ:
    print("Set the NUPIC environment variable.")
    exit(-1)
  if "NUPIC_CORE" not in os.environ:
    print("Set the NUPIC_CORE environment variable.")
    exit(-1)

  coreRelease = NupicCoreRelease(
    sys.argv[1:], 
    os.environ["NUPIC_CORE"]
  )
  nupicRelease = NupicRelease(
    sys.argv[1:], 
    os.environ["NUPIC"]
  )
  
  coreRelease.check()
  nupicRelease.check()

  
  coreReleaseSha = coreRelease.release()
  
  nupicRelease.release(coreReleaseSha)


