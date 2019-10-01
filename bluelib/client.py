# -*- coding: utf-8 -*-
"""
Base class for backend clients.
"""

import abc
import asyncio
import re
from typing import Callable, Any

class BaseBleClient(abc.ABC):
	"""docstring for BaseBleClient"""

	DEFAULT_MAXRETRIES              = 3
	DEFAULT_KEEP_CONNECTION         = False
	DEFAULT_TIMEOUT					= 30

	def __init__(self, address, loop=None, maxretries=DEFAULT_MAXRETRIES, 
		timeout=DEFAULT_TIMEOUT, defaultKeepConnection=DEFAULT_KEEP_CONNECTION):

		address = address.replace("-", ":").lower()

		if not re.match(
			"[0-9a-f]{2}([:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", address
		):
			raise Exception(
				"Mac address <{}> has the wrong format. Needs to be in hex and have delimiter ':' or '-'".format(
					address
				)
			)

		self.address = address
		self.loop = loop if loop else asyncio.get_event_loop()
		self.maxretries = maxretries
		self.timeout = timeout
		self.defaultKeepConnection = defaultKeepConnection

	# Async Context managers

	async def __aenter__(self):
		await self.connect()
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.disconnect()

	# Connectivity methods

	@abc.abstractmethod
	async def connect(self) -> bool:
		"""Connect to the specified GATT server.

		Returns:
			Boolean representing connection status.

		"""
		raise NotImplementedError()

	@abc.abstractmethod
	async def disconnect(self) -> bool:
		"""Disconnect from the specified GATT server.

		Returns:
			Boolean representing connection status.

		"""
		raise NotImplementedError()

	@abc.abstractmethod
	async def is_connected(self) -> bool:
		"""Check connection status between this client and the server.

		Returns:
			Boolean representing connection status.

		"""
		raise NotImplementedError()


	# GATT services methods

	# @abc.abstractmethod
	# async def get_services(self) -> Any:
	# 	"""Get all services registered for this GATT server.

	# 	Returns:
	# 	   Device's services tree.

	# 	"""
	# 	raise NotImplementedError()

	# I/O methods

	@abc.abstractmethod
	async def read_gatt_char(self, _uuid: str, **kwargs) -> bytearray:
		"""Perform read operation on the specified GATT characteristic.

		Args:
			_uuid (str or UUID): The uuid of the characteristics to read from.

		Returns:
			(bytearray) The read data.

		"""
		raise NotImplementedError()

	@abc.abstractmethod
	async def read_gatt_descriptor(self, handle: int, **kwargs) -> bytearray:
		"""Perform read operation on the specified GATT descriptor.

		Args:
			handle (int): The handle of the descriptor to read from.

		Returns:
			(bytearray) The read data.

		"""
		raise NotImplementedError()

	@abc.abstractmethod
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
		raise NotImplementedError()

	@abc.abstractmethod
	async def write_gatt_descriptor(
		self, handle: int, data: bytearray, **kwargs
	) -> Any:
		"""Perform a write operation on the specified GATT descriptor.

		Args:
			handle (int): The handle of the descriptor to read from.
			data (bytes or bytearray): The data to send.

		"""
		raise NotImplementedError()

	@abc.abstractmethod
	async def start_notify(
		self, _uuid: str, callback: Callable[[str, Any], Any], **kwargs
	) -> None:
		"""Activate notifications/indications on a characteristic.

		Callbacks must accept two inputs. The first will be a uuid string
		object and the second will be a bytearray.

		.. code-block:: python

			def callback(sender, data):
				print(f"{sender}: {data}")
			client.start_notify(char_uuid, callback)

		Args:
			_uuid (str or UUID): The uuid of the characteristics to start notification/indication on.
			callback (function): The function to be called on notification.

		"""
		raise NotImplementedError()

	@abc.abstractmethod
	async def stop_notify(self, _uuid: str) -> None:
		"""Deactivate notification/indication on a specified characteristic.

		Args:
			_uuid: The characteristic to stop notifying/indicating on.

		"""
		raise NotImplementedError()