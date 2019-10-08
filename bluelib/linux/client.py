import asyncio
import logging

from executor import Executor
from bluepy.btle import Peripheral, UUID, DefaultDelegate
from bluelib.client import BaseBleClient
from time import perf_counter
from typing import Callable, Any
from asyncio.events import AbstractEventLoop
from sys import _getframe

currentFuncName = lambda n=0: _getframe(n + 1).f_code.co_name

logger = logging.getLogger(__name__)

CCCD_UUID = "00002902-0000-1000-8000-00805f9b34fb"
CCCD_NOTIFY_VAL = b"\x01\x00"
CCCD_CLEAR = b"\x00\x00"

class CallbackList(object):
	def __init__(self):
		self.list = []

	def add(self, charHandle: int, func: Callable[[str, Any], Any]):
		for i in self.list:
			if i[0] == charHandle:
				i[1] = func
				return

		self.list.append((charHandle, func))


	def remove(self, charHandle: int):
		for i in self.list:
			if i[0] == charHandle:
				self.list.remove(i)


	def exec(self, charHandle: int, data: Any):
		for i in self.list:
			if i[0] == charHandle:
				return i[1](str(charHandle), data)

		raise Exception("Callback not found.")



class MyDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)
		self.callbacks = CallbackList()

	def handleNotification(self, cHandle, data):
		self.callbacks.exec(cHandle,data)



class BleClient(BaseBleClient):
	def __init__(self, address: str, loop: AbstractEventLoop = None, iface = 0, **kwargs):
		BaseBleClient.__init__(self, address, loop, **kwargs)

		self.client = None
		self.iface = 0
		self._execute = Executor(loop=loop)
		self._characteristics = None
		self._delegate = MyDelegate()


# %% Connectivity methods

	async def connect(self, retries=None, iface=None, **kwargs) -> bool:
		"""Connect to the specified GATT server.

		Returns:
			Boolean representing connection status.

		"""

		# Check if connection already exists
		if self.client is not None:
			try:
				if await self.is_connected():
					logger.debug(f"[{currentFuncName()}] device is already connected.")
					return True
				else:
					logger.debug(f"[{currentFuncName()}] device might has lost connection.")
			except Exception as e:
				self.logger.error(f"[{currentFuncName()}] received exception while checking connection state: " + str(e))


		# Adjust retries
		if retries is None:
			retries = self.maxretries

		# Adjust iface
		if iface is None:
			iface = self.iface

		# Try to connect
		for i in range(0,retries):
			try:
				t1 = perf_counter()
				self.client = await asyncio.wait_for(self._execute(Peripheral, self.address, "public", iface=iface), self.timeout)
				self._characteristics = None
				t2 = perf_counter() - t1

				self.client.withDelegate(self._delegate)

				logger.info(f"[{currentFuncName()}] connection established in {round(t2,2)}s in {i+1} of {retries} tries.")
				return True

			except Exception as e:
				del self.client
				self.client = None

				if (i+1) < retries:
					logger.warning(f"[{currentFuncName()}] failed to connect in {str(i+1)} of {str(retries)} tries." + " Received exception: " + str(e))
				else:
					logger.error(f"[{currentFuncName()}] could not connect to device." + " Received exception: " + str(e))
					raise e


	async def disconnect(self) -> bool:
		"""Disconnect from the specified GATT server.

		Returns:
			Boolean representing connection status.

		"""
		if self.client is not None:
			try:
				await self._execute(self.client.disconnect)
			except Exception as e:
				logger.debug(f"[{currentFuncName()}] received exception: {str(e)}")

			del self.client
			self.client = None
			#self._characteristics = None

		logger.debug(f"[{currentFuncName()}] disconnected.")

		return True



	async def is_connected(self):
		"""Check connection status between this client and the server.

		Returns:
			Boolean representing connection status.

		"""

		if self.client is not None:
			try:
				state = await asyncio.wait_for(self._execute(self.client.getState), self.timeout)
				return(state == 'conn')
			except Exception as e:
				logger.error(f"[{currentFuncName()}] received exception: {str(e)}")
		else:
			return False


	async def __check_connection(self) -> bool:
		try:
			if await self.is_connected():
				return True
		except:
			raise ConnectionError("Could not proof connecton.")

		logger.debug(f"[{currentFuncName(1)}] BLE device is not connected or connetion was lost. Trying to connect.")
		
		try:
			return await self.connect()
		except:
			raise ConnectionError("BLE device could not be connected or connection was lost and could not be reset")


# %% GATT services methods

	async def get_services(self) -> Any:
		"""Get all services registered for this GATT server.

		Returns:
		   Device's services tree.

		"""

		if self.client is not None:
			await self.__check_connection()
			services = await self._execute(self.client.getServices)
			return [str(s.uuid) for s in services]

		else:
			return None


# %% I/O methods

	async def _get_char(self, uuid: str):
		if self._characteristics is None:
			self._characteristics = await self._execute(self.client.getCharacteristics)

		_uuid = UUID(uuid)

		for c in self._characteristics:
			if c.uuid == _uuid:
				return c

		return None



	async def read_gatt_char(self, _uuid: str, **kwargs) -> bytearray:
		"""Perform read operation on the specified GATT characteristic.

		Args:
			_uuid (str or UUID): The uuid of the characteristics to read from.

		Returns:
			(bytearray) The read data.

		"""
		keepConnection = kwargs.get('keepConnection', None)

		try:
			await self.__check_connection()

			char = await self._get_char(_uuid)

			if char is None:
				raise Exception("Characteristic was not found.")

			data = await asyncio.wait_for(self._execute(char.read), self.timeout)

			if keepConnection is None:
				if self.defaultKeepConnection is False:
					await self.disconnect()
			elif keepConnection is False:
				await self.disconnect()

			logger.debug(f"[{currentFuncName(0)}] from characteristic \'{_uuid}\' received: {str(data)}")

			return data

		except Exception as e:
			raise e


	async def read_gatt_descriptor(self, handle: int, **kwargs) -> bytearray:
		"""Perform read operation on the specified GATT descriptor.

		Args:
			handle (int): The handle of the descriptor to read from.

		Returns:
			(bytearray) The read data.

		"""
		# TODO
		raise NotImplementedError()

		keepConnection = kwargs.get('keepConnection', None)

		try:
			await self.__check_connection()			

			# IMPLEMENTATION HERE #

			if keepConnection is None:
				if self.defaultKeepConnection is False:
					await self.disconnect()
			elif keepConnection is False:
				await self.disconnect()

			logger.debug(f"[{currentFuncName(0)}] from descriptor \'{str(handle)}\' received: {str(data)}")

			return data

		except Exception as e:
			raise e


	async def write_gatt_char(
		self, _uuid: str, data: bytearray, **kwargs
	) -> Any:
		"""Perform a write operation on the specified GATT characteristic.

		Args:
			_uuid (str or UUID): The uuid of the characteristics to write to.
			data (bytes or bytearray): The data to send.
			response (bool): If write-with-response operation should be done. Defaults to `False`.

		Returns:
			None if not `response=True`, in which case a bytearray is returned.

		"""
		keepConnection = kwargs.get('keepConnection', None)
		response = True

		try:
			await self.__check_connection()

			char = await self._get_char(_uuid)

			if char is None:
				raise Exception("Characteristic was not found.")

			data = bytes(data)
			ret = await asyncio.wait_for(self._execute(char.write, data, response), self.timeout)

			if keepConnection is None:
				if self.defaultKeepConnection is False:
					await self.disconnect()
			elif keepConnection is False:
				await self.disconnect()

			logger.debug(f"[{currentFuncName(0)}] to characteristic \'{_uuid}\' was sent: {str(data)}")
			if response:
				logger.debug(f"[{currentFuncName(0)}] characteristic \'{_uuid}\' responded: {str(ret)}")

			return ret

		except Exception as e:
			raise e


	async def write_gatt_descriptor(
		self, handle: int, data: bytearray, **kwargs
	) -> Any:
		"""Perform a write operation on the specified GATT descriptor.

		Args:
			handle (int): The handle of the descriptor to read from.
			data (bytes or bytearray): The data to send.

		"""
		# TODO
		raise NotImplementedError()

		keepConnection = kwargs.get('keepConnection', None)

		try:
			await self.__check_connection()			
			
			# IMPLEMENTATION HERE #

			if keepConnection is None:
				if self.defaultKeepConnection is False:
					await self.disconnect()
			elif keepConnection is False:
				await self.disconnect()

			logger.debug(f"[{currentFuncName(0)}] to descriptor \'{str(handle)}\' was sent: {str(data)}")
			logger.debug(f"[{currentFuncName(0)}] descriptor \'{str(handle)}\' responded: {str(ret)}")

			return ret

		except Exception as e:
			raise e


	async def start_notify(
		self, _uuid: str, callback: Callable[[str, Any], Any], **kwargs
	) -> None:
		"""Activate notifications/indications on a characteristic.

		Callbacks must accept two inputs. The first will be a uuid string
		object and the second will be a bytearray.

		.. code-block:: python

			def callback(sender, data):
			client.start_notify(char_uuid, callback)

		Args:
			_uuid (str or UUID): The uuid of the characteristics to start notification/indication on.
			callback (function): The function to be called on notification.

		"""
		try:
			await self.__check_connection()
			char = await self._get_char(_uuid)

			if char is None:
				raise Exception("Characteristic was not found.")

			descriptors = await asyncio.wait_for(self._execute(char.getDescriptors), self.timeout)

			cccd = None

			for d in descriptors:
				if d.uuid == UUID(CCCD_UUID):
					cccd = d

			if cccd is None:
				raise Exception(f"Could not start notify on {str(_uuid)}. CCCD was not found.")

			self._delegate.callbacks.add(char.getHandle(), callback)

			await asyncio.wait_for(self._execute(cccd.write, CCCD_NOTIFY_VAL, withResponse=True), self.timeout)
			resp = await asyncio.wait_for(self._execute(cccd.read), self.timeout)

			logger.debug(f"[{currentFuncName(0)}] started notify on characteristic {_uuid}. Response: {str(resp)}")

		except Exception as e:
			raise e


	async def stop_notify(self, _uuid: str, **kwargs) -> None:
		"""Deactivate notification/indication on a specified characteristic.

		Args:
			_uuid: The characteristic to stop notifying/indicating on.

		"""
		keepConnection = kwargs.get('keepConnection', None)

		try:
			await self.__check_connection()
			char = await self._get_char(_uuid)

			if char is None:
				raise Exception("Characteristic was not found.")

			descriptors = await asyncio.wait_for(self._execute(char.getDescriptors), self.timeout)

			cccd = None

			for d in descriptors:
				if d.uuid == UUID(CCCD_UUID):
					cccd = d

			if cccd is None:
				raise Exception(f"Could not stop notify on {str(_uuid)}. CCCD was not found.")

			self._delegate.callbacks.remove(char.getHandle())

			await asyncio.wait_for(self._execute(cccd.write, CCCD_CLEAR, withResponse=True), self.timeout)
			resp = await asyncio.wait_for(self._execute(cccd.read), self.timeout)

			if keepConnection is None:
				if self.defaultKeepConnection is False:
					await self.disconnect()
			elif keepConnection is False:
				await self.disconnect()

			logger.debug(f"[{currentFuncName(0)}] stopped notify on characteristic {_uuid}. Response: {str(resp)}")

		except Exception as e:
			raise e
