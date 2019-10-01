# -*- coding: utf-8 -*-

import sys
import pathlib

if str(pathlib.Path(__file__).parent) not in sys.path:
	sys.path.append(str(pathlib.Path(__file__).parent))