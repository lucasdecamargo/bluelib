from sensorlib.blesensor.blesensorbase import BleSensorBase
from sensorlib.blesensor.blesensorbase import currentFuncName
import asyncio

class Battery(BleSensorBase):

	# --- BATTERY SERVICE --- #
	BATTERY_BATTERY_LEVEL_CHAR_UUID     = "00002a19-0000-1000-8000-00805f9b34fb"
	
	def __init__(self, address, loop=None, **kwargs):
		super().__init__(address, loop, **kwargs)

		self.battery_BatteryLevel           = None

# %% Battery Service

	async def get_battery_BatteryLevel(self, **kwargs):
		try:
			data = await self._get_notify(Battery.BATTERY_BATTERY_LEVEL_CHAR_UUID, **kwargs)
			self.battery_BatteryLevel = int(format(data[0]))
			self.logger.info("[" + currentFuncName() + "] received: " + str(self.battery_BatteryLevel))

			return self.battery_BatteryLevel

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e

			