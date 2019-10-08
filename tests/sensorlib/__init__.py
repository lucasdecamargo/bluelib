# -*- coding: utf-8 -*-

import sys
import pathlib

_module_path = pathlib.Path(__file__).parent.parent
if str(_module_path) not in sys.path:
	sys.path.append(str(_module_path))

import sensorlib.blesensor