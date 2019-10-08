# -*- coding: utf-8 -*-

import sys
import platform
import pathlib

_module_path = pathlib.Path(__file__).parent.parent
if str(_module_path) not in sys.path:
	sys.path.append(str(_module_path))

if platform.system() == "Windows":
	import bleak
	from bleak.backends.dotnet.discovery import discover as scan
	from bluelib.windowslib.client import BleClient


if platform.system() == "Linux":
	from bluelib.linux.scan import scan
	from bluelib.linux.client import BleClient
