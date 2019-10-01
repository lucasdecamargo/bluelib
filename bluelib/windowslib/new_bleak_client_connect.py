# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 15:13:03 2019

@author: sdr
"""

import logging
import asyncio
from asyncio.events import AbstractEventLoop
from functools import wraps
from typing import Callable, Any

from bleak.exc import BleakError, BleakDotNetTaskError
from bleak.backends.client import BaseBleakClient
from bleak.backends.dotnet.discovery import discover
from bleak.backends.dotnet.utils import (
	wrap_Task,
	wrap_IAsyncOperation,
	IAsyncOperationAwaitable,
)
from bleak.backends.service import BleakGATTServiceCollection
from bleak.backends.dotnet.service import BleakGATTServiceDotNet
from bleak.backends.dotnet.characteristic import BleakGATTCharacteristicDotNet
from bleak.backends.dotnet.descriptor import BleakGATTDescriptorDotNet


# Import of other CLR components needed.
from System import Array, Byte
from Windows.Foundation import IAsyncOperation, TypedEventHandler
from Windows.Storage.Streams import DataReader, DataWriter, IBuffer
from Windows.Devices.Bluetooth import (
	BluetoothLEDevice,
	BluetoothConnectionStatus,
	BluetoothCacheMode,
)
from Windows.Devices.Bluetooth.GenericAttributeProfile import (
	GattDeviceService,
	GattDeviceServicesResult,
	GattCharacteristic,
	GattCharacteristicsResult,
	GattDescriptor,
	GattDescriptorsResult,
	GattCommunicationStatus,
	GattReadResult,
	GattWriteResult,
	GattValueChangedEventArgs,
	GattCharacteristicProperties,
	GattClientCharacteristicConfigurationDescriptorValue,
)

logger = logging.getLogger(__name__)

async def connect(self, timeout=2) -> bool:
	"""Connect to the specified GATT server.

	Returns:
		Boolean representing connection status.

	"""
	# Try to find the desired device.
	devices = await discover(timeout, loop=self.loop)
	sought_device = list(
		filter(lambda x: x.address.upper() == self.address.upper(), devices)
	)

	if len(sought_device):
		self._device_info = sought_device[0].details
	else:
		raise BleakError(
			"Device with address {0} was " "not found.".format(self.address)
		)

	logger.debug("Connecting to BLE device @ {0}".format(self.address))
	self._requester = await wrap_IAsyncOperation(
		IAsyncOperation[BluetoothLEDevice](
			BluetoothLEDevice.FromIdAsync(self._device_info.Id)
		),
		return_type=BluetoothLEDevice,
		loop=self.loop,
	)

	def _ConnectionStatusChanged_Handler(sender, args):
		logger.debug("_ConnectionStatusChanged_Handler: " + args.ToString())

	self._requester.ConnectionStatusChanged += _ConnectionStatusChanged_Handler

	# Obtain services, which also leads to connection being established.
	await self.get_services()
	await asyncio.sleep(0.2, loop=self.loop)
	connected = await self.is_connected()
	if connected:
		logger.debug("Connection successful.")
	else:
		raise BleakError(
			"Connection to {0} was not successful!".format(self.address)
		)

	return connected


def disconnect(self) -> None:
	"""Disconnect from the specified GATT server.

	Returns:
		Boolean representing connection status.

	"""
	logger.debug("Disconnecting from BLE device...")
	# Remove notifications
	# TODO: Make sure all notifications are removed prior to Dispose.
	# Dispose all components that we have requested and created.
	for service in self.services:
		# for characteristic in service.characteristics:
		#     for descriptor in characteristic.descriptors:
		#         descriptor.obj.Dispose()
		#     characteristic.obj.Dispose()
		service.obj.Dispose()
	self.services = BleakGATTServiceCollection()
	self._requester.Dispose()
	self._requester = None

	return