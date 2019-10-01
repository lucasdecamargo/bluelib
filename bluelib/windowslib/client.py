# -*- coding: utf-8 -*-

import asyncio
from asyncio.events import AbstractEventLoop
from typing import Callable, Any
import pathlib
import sys
import bleak
import types
import new_bleak_client_connect
import logging
import time

from bluelib.client import BaseBleClient

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name


class BleClient(BaseBleClient):
	def __init__(self, address: str, loop: AbstractEventLoop = None, logger = None, **kwargs):
		BaseBleClient.__init__(self, address, loop, **kwargs)

		self.client = None

		if logger is None:
			logger = logging.getLogger(__name__ + " dev "  + str(self.address))
			logger.addHandler(logging.NullHandler())

		self.logger = logger


	def __del__(self):
		if self.client is not None:
			del self.client
			self.client = None


# %% Connectivity methods

	async def connect(self, timeout=2, retries=None) -> bool:
		"""Connect to the specified GATT server.

		Returns:
			Boolean representing connection status.

		"""
		if self.client is not None:
			try:
				if await asyncio.wait_for(self.is_connected(), self.timeout):
					self.logger.debug("Devices is already connected.")
					return True
			except Exception as e:
				self.logger.error(f"[BleClient.{currentFuncName()}] received exception: " + str(e))

		if retries is None:
			retries = self.maxretries

		for i in range(0,retries):
			try:
				self.client = bleak.BleakClient(self.address, self.loop)

				# Overrides the bleak connect method #
				self.client.connect = types.MethodType(new_bleak_client_connect.connect, self.client)

				t1 = time.perf_counter()
				status = await asyncio.wait_for(self.client.connect(timeout=timeout), self.timeout)
				t2 = time.perf_counter() - t1
				self.logger.info(f"[BleClient.{currentFuncName()}] connection established in {round(t2,2)}s in {i+1} of {retries} tries.")
				return status

			except Exception as e:
				del self.client
				self.client = None

				if (i+1) < retries:
					self.logger.warning(f"[BleClient.{currentFuncName()}] failed to connect in {str(i+1)} of {str(retries)} tries." + " Received exception: " + str(e))
				else:
					self.logger.error(f"[BleClient.{currentFuncName()}] could not connect to device." + " Received exception: " + str(e))
					raise e


	async def __check_connection(self) -> bool:
		try:
			if self.client is not None:
				if await asyncio.wait_for(self.client.is_connected(), self.timeout):
					return True

			self.logger.debug(f"[BleClient.{currentFuncName(1)}] BLE device is not connected or connetion was lost. Trying to connect.")
			status = await self.connect()

			if not status:
				raise ConnectionError("BLE device could not be connected or connection was lost and could not be reset")

			return status

		except Exception as e:
			raise e


	async def disconnect(self) -> bool:
		"""Disconnect from the specified GATT server.

		Returns:
			Boolean representing connection status.

		"""
		status = False

		try:
			status = await asyncio.wait_for(self.client.disconnect(), self.timeout)
		except Exception as e:
			self.logger.debug(f"[BleClient.{currentFuncName()}] received exception: " + str(e))
			pass

		del self.client
		self.client = None
		self.logger.debug(f"[BleClient.{currentFuncName()}] disconnected.")
		return status


	async def is_connected(self) -> bool:
		"""Check connection status between this client and the server.

		Returns:
			Boolean representing connection status.

		"""
		if self.client is not None:
			return await self.client.is_connected()
		else:
			return False


# %% GATT services methods

	# async def get_services(self, **kwargs) -> Any:
	# 	"""Get all services registered for this GATT server.

	# 	Returns:
	# 	   Device's services tree.

	# 	"""
	# 	keepConnection = kwargs.get('keepConnection', None)

	# 	try:
	# 		await self.__check_connection()			
	# 		data = await asyncio.wait_for(self.client.get_services(), self.timeout)

	# 		if keepConnection is None:
	# 			if self.defaultKeepConnection is False:
	# 				await self.disconnect()
	# 		elif keepConnection is False:
	# 			await self.disconnect()

	# 		self.logger.debug(f"[BleClient.{currentFuncName(0)}] received: {str(data)}")

	# 		return data

	# 	except Exception as e:
	# 		raise e

	
# %% I/O methods

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
			data = await asyncio.wait_for(self.client.read_gatt_char(_uuid, **kwargs), self.timeout)

			if keepConnection is None:
				if self.defaultKeepConnection is False:
					await self.disconnect()
			elif keepConnection is False:
				await self.disconnect()

			self.logger.debug(f"[BleClient.{currentFuncName(0)}] from characteristic \'{_uuid}\' received: {str(data)}")

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
		keepConnection = kwargs.get('keepConnection', None)

		try:
			await self.__check_connection()			
			data = await asyncio.wait_for(self.client.read_gatt_descriptor(handle, **kwargs), self.timeout)

			if keepConnection is None:
				if self.defaultKeepConnection is False:
					await self.disconnect()
			elif keepConnection is False:
				await self.disconnect()

			self.logger.debug(f"[BleClient.{currentFuncName(0)}] from descriptor \'{str(handle)}\' received: {str(data)}")

			return data

		except Exception as e:
			raise e


	async def write_gatt_char(
		self, _uuid: str, data: bytearray, response: bool = False, **kwargs
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

		try:
			await self.__check_connection()			
			ret = await asyncio.wait_for(self.client.write_gatt_char(_uuid, data, response), self.timeout)

			if keepConnection is None:
				if self.defaultKeepConnection is False:
					await self.disconnect()
			elif keepConnection is False:
				await self.disconnect()

			self.logger.debug(f"[BleClient.{currentFuncName(0)}] to characteristic \'{_uuid}\' was sent: {str(data)}")
			if response:
				self.logger.debug(f"[BleClient.{currentFuncName(0)}] characteristic \'{_uuid}\' responded: {str(ret)}")

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
		keepConnection = kwargs.get('keepConnection', None)

		try:
			await self.__check_connection()			
			ret = await asyncio.wait_for(self.client.write_gatt_descriptor(handle, data), self.timeout)

			if keepConnection is None:
				if self.defaultKeepConnection is False:
					await self.disconnect()
			elif keepConnection is False:
				await self.disconnect()

			self.logger.debug(f"[BleClient.{currentFuncName(0)}] to descriptor \'{str(handle)}\' was sent: {str(data)}")
			self.logger.debug(f"[BleClient.{currentFuncName(0)}] descriptor \'{str(handle)}\' responded: {str(ret)}")

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
			await asyncio.wait_for(self.client.start_notify(_uuid, callback, **kwargs), self.timeout)
			self.logger.debug(f"[BleClient.{currentFuncName(0)}] started notify on characteristic {_uuid}.")

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
			ret = await asyncio.wait_for(self.client.stop_notify(_uuid), self.timeout)

			if keepConnection is None:
				if self.defaultKeepConnection is False:
					await self.disconnect()
			elif keepConnection is False:
				await self.disconnect()

			self.logger.debug(f"[BleClient.{currentFuncName(0)}] stopped notify on characteristic {_uuid}.")

			return ret

		except Exception as e:
			raise e

