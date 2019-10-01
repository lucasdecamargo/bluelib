import asyncio

from asyncio.events import AbstractEventLoop
from bluepy.btle import Scanner, ScanEntry
from executor import Executor

async def scan(timeout=2, loop: AbstractEventLoop = asyncio.get_event_loop()):
	scanner = Scanner(0)

	execute = Executor(loop=loop)

	devices = await execute(scanner.scan, timeout)

	dev_list = []

	for d in devices:
		dev_list.append({"address": d.addr,
						 "name": d.getValueText(ScanEntry.COMPLETE_LOCAL_NAME),
						 "rssi": d.rssi})

	return dev_list