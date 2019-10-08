from sensorlib.blesensor.blesensorbase import BleSensorBase
from sensorlib.blesensor.blesensorbase import currentFuncName
import struct
import time
import asyncio

class Temperature(BleSensorBase):
	
	# --- TEMPERATURE SERVICE --- #
	TEMP_TEMPERATURE_CHAR_UUID          = "00002100-0000-1000-8000-00805F9B575A".lower()
	TEMP_CALIBRATION_DATA_CHAR_UUID     = "00002101-0000-1000-8000-00805F9B575A".lower()

	def __init__(self, address, loop=None, **kwargs):
		super().__init__(address, loop, **kwargs)

		self.temp_Temperature               = None
		self.temp_CalibrationData_CalA      = None
		self.temp_CalibrationData_CalB      = None
		self.temp_CalibrationData_CalDate   = None


# %% Temperature Service

	async def get_temp_Temperature(self, **kwargs):
		try:
			self._lock_Temperature = True
			data = await self._get_notify(Temperature.TEMP_TEMPERATURE_CHAR_UUID, **kwargs)
			self.temp_Temperature = struct.unpack('<f',data)[0]

			self.logger.info("[" + currentFuncName() + "] received: " + str(self.temp_Temperature))

			return self.temp_Temperature

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_temp_CalibrationData(self, **kwargs):
		if self.temp_CalibrationData_CalA is not None:
			return list((self.temp_CalibrationData_CalA, self.temp_CalibrationData_CalB)), self.temp_CalibrationData_CalDate

		try:
			caldata = await self.client.read_gatt_char(Temperature.TEMP_CALIBRATION_DATA_CHAR_UUID, **kwargs)

			self.temp_CalibrationData_CalA = struct.unpack('>H',caldata[:2])[0]
			self.temp_CalibrationData_CalB = struct.unpack('>h',caldata[2:4])[0]

			i = 0
			date = ""
			for i in range(4):
				date = date + str(chr(caldata[i + 4]))
			date = date + "/"
			for i in range(2):
				date = date + str(chr(caldata[i + 8]))
			date = date + "/"
			for i in range(2):
				date = date + str(chr(caldata[i + 10]))

			self.temp_CalibrationData_CalDate = date

			self.logger.info("[" + currentFuncName() + "] received: "
				+ f"calA: {self.temp_CalibrationData_CalA}\t"
				+ f"calB: {self.temp_CalibrationData_CalB}\t"
				+ f"calDate: {self.temp_CalibrationData_CalDate}")

			return list((self.temp_CalibrationData_CalA, self.temp_CalibrationData_CalB)), self.temp_CalibrationData_CalDate

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def set_temp_CalibrationData(self, calA, calB, **kwargs):
		try:
			# Write A and B to bytearray:
			caldata = bytearray([39, 16, 0, 0, 49, 57, 55, 48, 48, 49, 48, 49])
			caldata[0] = np.uint8(calA >> 8)
			caldata[1] = np.uint8(calA & 0x00FF)
			caldata[2] = np.uint8(calB >> 8)
			caldata[3] = np.uint8(calB & 0x00FF)
			calDate = bytearray(time.strftime("%Y%m%d"), "utf-8")

			# Write actual date to bytearray:
			i = 0
			for i in range(8):
				caldata[4 + i] = calDate[i]

			await self.client.write_gatt_char(Temperature.TEMP_CALIBRATION_DATA_CHAR_UUID, caldata, **kwargs)

			self.temp_CalibrationData_CalA = calA
			self.temp_CalibrationData_CalB = calB
			self.temp_CalibrationData_CalDate = calDate

			self.logger.info("[" + currentFuncName() + "] transmitted: "
				+ f"calA: {self.temp_CalibrationData_CalA}\t"
				+ f"calB: {self.temp_CalibrationData_CalB}\t"
				+ f"calDate: {self.temp_CalibrationData_CalDate}")

			return list((self.temp_CalibrationData_CalA, self.temp_CalibrationData_CalB)), self.temp_CalibrationData_CalDate

		except Exception as e:
			self.temp_CalibrationData_CalA = None
			self.temp_CalibrationData_CalB = None
			self.temp_CalibrationData_CalDate = None
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e