import logging
import asyncio
import sys
import os
import pathlib

_module_path = pathlib.Path(__file__).parent.parent
if str(_module_path) not in sys.path:
    sys.path.append(str(_module_path))

from tSense_lib import tSense
from termcolor import colored

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

async def main(loop):
    import time

    time.sleep(10)

    sensors = [tSense("57:5a:4c:f3:7a:1c", loop=loop, defaultKeepConnection=False),
               tSense("57:5a:4c:f3:7a:0a", loop=loop, defaultKeepConnection=False),
               tSense("57:5a:4c:12:b5:52", loop=loop, defaultKeepConnection=False),
               tSense("57:5a:4c:f3:7a:19", loop=loop, defaultKeepConnection=False),
               tSense("57:5a:4c:d2:14:16", loop=loop, defaultKeepConnection=False),
               #tSense("57:5a:4c:f3:7a:1e", loop=loop, defaultKeepConnection=False)
               ]

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(
                '%(asctime)-15s %(name)s %(levelname)s %(message)s'))
    sh.setLevel(logging.DEBUG)

    # sensor.logger.addHandler(sh)
    # sensor.logger.setLevel(logging.DEBUG)
    # sensor.client.logger.addHandler(sh)
    # sensor.client.logger.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(sh)
    root_logger.setLevel(logging.DEBUG)

    async def method(s,loop):
        await s.connect(retries=1)
        await s.get_temp_Temperature(keepConnection=True)
        await asyncio.sleep(2,loop=loop)
        #await s.get_temp_CalibrationData(keepConnection=True)
        await s.set_genSens_Label("Sensor for testing", keepConnection=True)
        await s.measure(["temperature", "battery"])
        await s.client.disconnect()

    def colored2(text,color):
        if color is 'red':
            print(bcolors.WARNING + text + bcolors.ENDC)

    
    print(colored("### Connecting...", 'red'))
    t1 = time.perf_counter()

    tasks = []
    for sensor in sensors:
        tasks.append(sensor.connect())
    await asyncio.wait(tasks)

    t2 = time.perf_counter() - t1
    print(colored(f"### Done in {round(t2,2)}s", 'red'))


    await asyncio.sleep(2,loop=loop)
    print(colored("### Requesting temperature...", 'red'))
    t1 = time.perf_counter()

    tasks = []
    for sensor in sensors:
        tasks.append(sensor.get_temp_Temperature(keepConnection=True))
    await asyncio.wait(tasks)

    t2 = time.perf_counter() - t1
    print(colored(f"### Done in {round(t2,2)}s", 'red'))



    await asyncio.sleep(2,loop=loop)
    print(colored("### Setting label...", 'red'))
    t1 = time.perf_counter()

    tasks = []
    for sensor in sensors:
        tasks.append(sensor.set_genSens_Label("Test Sensor", keepConnection=False))
    await asyncio.wait(tasks)

    t2 = time.perf_counter() - t1
    print(colored(f"### Done in {round(t2,2)}s", 'red'))


    await asyncio.sleep(2,loop=loop)
    print(colored("### Measuring...", 'red'))
    t1 = time.perf_counter()

    tasks = []
    for sensor in sensors:
        tasks.append(sensor.measure(["temperature", "battery"]))
    await asyncio.wait(tasks)

    t2 = time.perf_counter() - t1
    print(colored(f"### Done in {round(t2,2)}s", 'red'))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))