import abc
import bluelib
import sys
import time
import logging
import asyncio

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class BleSensorBase(abc.ABC):

	DEFAULT_MAXRETRIES              = 3
	DEFAULT_KEEP_CONNECTION         = False
	DEFUALT_TIMEOUT					= 30

	 # ----- BLE UUID STATIC DEFINITIONS ----- #

	# --- GENERIC ACCESS SERVICE --- #
	GEN_ACC_DEVICE_NAME_CHAR_UUID       = "00002a00-0000-1000-8000-00805f9b34fb"


	def __init__(self, address, loop=None,
		maxretries = DEFAULT_MAXRETRIES,
		defaultKeepConnection = DEFAULT_KEEP_CONNECTION,
		timeout = DEFUALT_TIMEOUT):

		self.logger = logging.getLogger(str(self.__class__.__name__)
				+ " dev "
				+ str(address).replace("-", ":"))
		self.logger.addHandler(logging.NullHandler())

		
		self.client = bluelib.BleClient(address, loop=loop,
			maxretries=maxretries ,timeout=timeout, defaultKeepConnection=defaultKeepConnection)

		self.loop = loop if loop else asyncio.get_event_loop()

		self.genAcc_DeviceName = None

	
	@staticmethod
	async def scan(time=5, filter:str=None, sensor=None):
		if sensor is not None:
			logger = sensor.logger
		else:
			logger = logging.getLogger()
		try:
			devices = await bluelib.scan(time)
			ret = []

			for d in devices:
				if filter is not None:
					if filter in str(d):
					   logger.info("BleSensor [" + currentFuncName() + "] scanned device: " + str(d))
					   ret.append(str(d))
				else:
					logger.info("BleSensor [" + currentFuncName() + "] scanned device: " + str(d))
					ret.append(str(d))

			return ret

		except Exception as e:
			logger.error("BleSensor [" + currentFuncName() + "] received exception: " + str(e))
			raise e


	def get_address(self):
		return self.client.address


	async def connect(self, timeout=None, retries=None) -> bool:
		try:
			t1 = time.perf_counter()
			status = await self.client.connect(timeout=timeout, retries=retries)
			t2 = time.perf_counter() - t1
			self.logger.info(f"[{currentFuncName()}] connection established in {round(t2,2)}s.")
			return status
		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e

	async def disconnect(self) -> bool:
		return await self.client.disconnect()

	async def is_connected(self) -> bool:
		return await self.client.is_connected()


	async def get_genAcc_DeviceName(self, **kwargs):
		if self.genAcc_DeviceName is not None:
			return self.genAcc_DeviceName

		try:
			data = await self.client.read_gatt_char(BleSensorBase.GEN_ACC_DEVICE_NAME_CHAR_UUID, **kwargs)
			self.genAcc_DeviceName = data.decode("utf-8").strip(" ")
			self.logger.info("[" + currentFuncName() + "] received: " + self.genAcc_DeviceName)
			return self.genAcc_DeviceName

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			return None


	async def _get_notify(self, _uuid, **kwargs):

		lock = True
		data = None

		delay = kwargs.get('delay',0.2)
		timeout = kwargs.get('timeout',2)

		def __callback(_sender, _data):
			nonlocal lock
			nonlocal data
			data = _data
			lock = False

		try:
			await self.client.start_notify(_uuid, __callback, **kwargs)

			start = time.perf_counter()
			while lock:
				await asyncio.sleep(delay, self.loop)
				if time.perf_counter() > start + timeout:
					lock = False
					raise ConnectionError("Timeout: BLE connection might be broken.")

			await self.client.stop_notify(_uuid, **kwargs)

			return data

		except Exception as e:
			raise e
