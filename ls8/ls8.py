#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

argv = sys.argv

if len(argv) != 2:
    print('python ls8 (Source File)')
    exit()
else:
    cpu = CPU()
    cpu.load(argv[1])
    cpu.run()
