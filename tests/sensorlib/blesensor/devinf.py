from sensorlib.blesensor.blesensorbase import BleSensorBase
from sensorlib.blesensor.blesensorbase import currentFuncName
import asyncio

class DeviceInformation(BleSensorBase):

	# --- DEVICE INFORMATION SERVICE --- #
	DEV_INF_MANUFACTURER_NAME_CHAR_UUID = "00002a29-0000-1000-8000-00805f9b34fb"
	DEV_INF_MODEL_NUMBER_CHAR_UUID      = "00002a24-0000-1000-8000-00805f9b34fb"
	DEV_INF_SERIAL_NUMBER_CHAR_UUID     = "00002a25-0000-1000-8000-00805f9b34fb"
	DEV_INF_HARDWARE_REVISION_CHAR_UUID = "00002a27-0000-1000-8000-00805f9b34fb"
	DEV_INF_FIRMWARE_REVISION_CHAR_UUID = "00002a26-0000-1000-8000-00805f9b34fb"
	DEV_INF_SOFTWARE_REVISION_CHAR_UUID = "00002a28-0000-1000-8000-00805f9b34fb"
	DEV_INF_SYSTEM_ID_CHAR_UUID         = "00002a23-0000-1000-8000-00805f9b34fb"
	DEV_INF_IEEE_RCDL_CHAR_UUID         = "00002a2a-0000-1000-8000-00805f9b34fb"
	DEV_INF_PNP_ID_CHAR_UUID            = "00002a50-0000-1000-8000-00805f9b34fb"

	def __init__(self, address, loop=None, **kwargs):
		super().__init__(address, loop, **kwargs)

		self.devInf_ManufacturerName        = None
		self.devInf_ModelNumber             = None
		self.devInf_SerialNumber            = None
		self.devInf_HardwareRevision        = None
		self.devInf_FirmwareRevision        = None
		self.devInf_SoftwareRevision        = None
		self.devInf_SystemID                = None
		self.devInf_IEEE_RCDL               = None
		self.devInf_PNP_ID                  = None


	async def get_devInf_ManufacturerName(self, **kwargs):
		if self.devInf_ManufacturerName is not None:
			return self.devInf_ManufacturerName

		try:
			data = await self.client.read_gatt_char(DeviceInformation.DEV_INF_MANUFACTURER_NAME_CHAR_UUID, **kwargs)
			self.devInf_ManufacturerName = data.decode("utf-8").strip(" ")
			self.logger.info("[" + currentFuncName() + "] received: " + self.devInf_ManufacturerName)

			return self.devInf_ManufacturerName

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_devInf_ModelNumber(self, **kwargs):
		if self.devInf_ModelNumber is not None:
			return self.devInf_ModelNumber

		try:
			data = await self.client.read_gatt_char(DeviceInformation.DEV_INF_MODEL_NUMBER_CHAR_UUID, **kwargs)
			self.devInf_ModelNumber = data.decode("utf-8").strip(" ")
			self.logger.info("[" + currentFuncName() + "] received: " + self.devInf_ModelNumber)

			return self.devInf_ModelNumber

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_devInf_SerialNumber(self, **kwargs):
		if self.devInf_SerialNumber is not None:
			return self.devInf_SerialNumber

		try:
			data = await self.client.read_gatt_char(DeviceInformation.DEV_INF_SERIAL_NUMBER_CHAR_UUID, **kwargs)
			self.devInf_SerialNumber = data.decode("utf-8").strip(" ")
			self.logger.info("[" + currentFuncName() + "] received: " + self.devInf_SerialNumber)

			return self.devInf_SerialNumber

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_devInf_HardwareRevision(self, **kwargs):
		if self.devInf_HardwareRevision is not None:
			return self.devInf_HardwareRevision

		try:
			data = await self.client.read_gatt_char(DeviceInformation.DEV_INF_HARDWARE_REVISION_CHAR_UUID, **kwargs)
			self.devInf_HardwareRevision = data.decode("utf-8").strip(" ")
			self.logger.info("[" + currentFuncName() + "] received: " + self.devInf_HardwareRevision)

			return self.devInf_HardwareRevision

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_devInf_FirmwareRevision(self, **kwargs):
		if self.devInf_FirmwareRevision is not None:
			return self.devInf_FirmwareRevision

		try:
			data = await self.client.read_gatt_char(DeviceInformation.DEV_INF_FIRMWARE_REVISION_CHAR_UUID, **kwargs)
			self.devInf_FirmwareRevision = data.decode("utf-8").strip(" ")
			self.logger.info("[" + currentFuncName() + "] received: " + self.devInf_FirmwareRevision)

			return self.devInf_FirmwareRevision

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_devInf_SoftwareRevision(self, **kwargs):
		if self.devInf_SoftwareRevision is not None:
			return self.devInf_SoftwareRevision

		try:
			data = await self.client.read_gatt_char(DeviceInformation.DEV_INF_SOFTWARE_REVISION_CHAR_UUID, **kwargs)
			self.devInf_SoftwareRevision = data.decode("utf-8").strip(" ")
			self.logger.info("[" + currentFuncName() + "] received: " + self.devInf_SoftwareRevision)

			return self.devInf_SoftwareRevision

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_devInf_SystemID(self, **kwargs):
		if self.devInf_SystemID is not None:
			return self.devInf_SystemID

		try:
			data = await self.client.read_gatt_char(DeviceInformation.DEV_INF_SYSTEM_ID_CHAR_UUID, **kwargs)
			self.devInf_SystemID = data # Has to be formated
			self.logger.info("[" + currentFuncName() + "] received: " + str(self.devInf_SystemID))

			return self.devInf_SystemID

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_devInf_IEEE_RCDL(self, **kwargs):
		if self.devInf_IEEE_RCDL is not None:
			return self.devInf_IEEE_RCDL

		try:
			data = await self.client.read_gatt_char(DeviceInformation.DEV_INF_IEEE_RCDL_CHAR_UUID, **kwargs)
			self.devInf_IEEE_RCDL = data # Has to be formated
			self.logger.info("[" + currentFuncName() + "] received: " + str(self.devInf_IEEE_RCDL))

			return self.devInf_IEEE_RCDL

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_devInf_PNP_ID(self, **kwargs):
		if self.devInf_PNP_ID is not None:
			return self.devInf_PNP_ID

		try:
			data = await self.client.read_gatt_char(DeviceInformation.DEV_INF_PNP_ID_CHAR_UUID, **kwargs)
			self.devInf_PNP_ID = data # Has to be formated
			self.logger.info("[" + currentFuncName() + "] received: " + str(self.devInf_PNP_ID))

			return self.devInf_PNP_ID

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_devInf(self, **kwargs):
		keepConnection = kwargs.get('keepConnection',None)
		kwargs['keepConnection'] = True

		try:
			await self.get_devInf_ManufacturerName(**kwargs)
		except:
			pass
		try:
			await self.get_devInf_ModelNumber(**kwargs)
		except:
			pass
		try:
			await self.get_devInf_SerialNumber(**kwargs)
		except:
			pass
		try:
			await self.get_devInf_HardwareRevision(**kwargs)
		except:
			pass
		try:
			await self.get_devInf_FirmwareRevision(**kwargs)
		except:
			pass
		try:
			await self.get_devInf_SoftwareRevision(**kwargs)
		except:
			pass
		try:
			await self.get_devInf_SystemID(**kwargs)
		except:
			pass
		try:
			await self.get_devInf_IEEE_RCDL(**kwargs)
		except:
			pass

		kwargs['keepConnection'] = keepConnection
		try:
			await self.get_devInf_PNP_ID(**kwargs)
		except:
			pass
