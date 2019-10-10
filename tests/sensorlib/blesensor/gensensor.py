from sensorlib.blesensor.blesensorbase import BleSensorBase
from sensorlib.blesensor.blesensorbase import currentFuncName
#from numpy import uint8
import asyncio

def uint8(val):
	return val.to_bytes(1,byteorder='little', signed=False)

class GenericSensor(BleSensorBase):

	# ---- DEFINITIONS RELATED TO THE GENERIC SENSOR SERVICE ---- #
	# -- Please use this values to use the following methods:
	# --- GenericSensor.set_genSens_AdvMode(<GenericSensor.ADV_MODE_*>)
	# --- GenericSensor.set_genSens_TxPwrLvl(<GenericSensor.TX_PWR_LVL_*>, <GenericSensor.TX_PWR_LVL_*>)
	# ---- ADVERTISEMENT MODES ---- #
	ADV_MODE_1 = 0
	ADV_MODE_2 = 1
	ADV_MODE_3 = 2
	ADV_MODE_4 = 3
	# ---- MAXIMUM ADVERTISEMENT INTERVALS ---- #
	MAX_ADV_INTERVAL_MODE_1         = 0.5
	MAX_ADV_INTERVAL_MODE_2         = 1.250
	MAX_ADV_INTERVAL_MODE_3         = 2.5
	MAX_ADV_INTERVAL_MODE_4         = 5
	# ---- TX POWER LEVELS ---- #
	TX_PWR_LVL_NEG_18_DBM = 1
	TX_PWR_LVL_NEG_12_DBM = 2
	TX_PWR_LVL_NEG_6_DBM = 3
	TX_PWR_LVL_NEG_3_DBM = 4
	TX_PWR_LVL_NEG_2_DBM = 5
	TX_PWR_LVL_NEG_1_DBM = 6
	TX_PWR_LVL_0_DBM = 7
	TX_PWR_LVL_3_DBM = 8
	TX_PWR_LVL_MAX = 9
	# ----------------------------------------------------------- #

	# --- GENERIC SENSOR SERVICE --- #
	GEN_SENS_LABEL_CHAR_UUID            = "00002000-0000-1000-8000-00805F9B575A".lower()
	GEN_SENS_ADV_MODE_CHAR_UUID         = "00002001-0000-1000-8000-00805F9B575A".lower()
	GEN_SENS_TX_PWR_LVL_CHAR_UUID       = "00002002-0000-1000-8000-00805F9B575A".lower()

	def __init__(self, address, loop=None, **kwargs):
		super().__init__(address, loop, **kwargs)

		self.connTimeout 					= None
		self.connTimeout_plus 				= 0.5

		self.genSens_Label                  = None
		self.genSens_AdvMode                = None
		self.genSens_TxPwrLvl_AdvScan       = None
		self.genSens_TxPwrLvl_Conn          = None

	
	async def connect(self, timeout=None, retries=None) -> bool:
		try:
			if timeout is None:
				timeout = self.connTimeout
			if timeout is None:
				status = await BleSensorBase.connect(self, timeout=(GenericSensor.MAX_ADV_INTERVAL_MODE_4 + self.connTimeout_plus), retries=retries)
				if status:
					await self.get_genSens_AdvMode(keepConnection=True)
				return status
			else:
				return await BleSensorBase.connect(self, timeout=timeout, retries=retries)
		except Exception as e:
			raise e


	# %% Generic Sensor Service
	async def get_genSens_Label(self, **kwargs):
		if self.genSens_Label is not None:
			return self.genSens_Label

		try:
			data = await self.client.read_gatt_char(GenericSensor.GEN_SENS_LABEL_CHAR_UUID, **kwargs)
			self.genSens_Label = data.decode("utf-8").strip(" ")
			self.logger.info("[" + currentFuncName() + "] received: " + self.genSens_Label)
			return self.genSens_Label

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def set_genSens_Label(self, label, **kwargs):
		if len(label) <= 64:
			newLabel = label
		else:
			newLabel = label[:64]

		bytelist = bytearray(newLabel,"utf-8")

		try:
			data = await self.client.write_gatt_char(GenericSensor.GEN_SENS_LABEL_CHAR_UUID, bytelist, **kwargs)
			self.genSens_Label = newLabel
			self.logger.info("[" + currentFuncName() + "] transmitted: " + self.genSens_Label)
			return self.genSens_Label

		except Exception as e:
			self.genSens_Label = None
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_genSens_AdvMode(self, **kwargs):
		if self.genSens_AdvMode is not None:
			return self.genSens_AdvMode

		try:
			data = await self.client.read_gatt_char(GenericSensor.GEN_SENS_ADV_MODE_CHAR_UUID, **kwargs)

			self.genSens_AdvMode = int(format(data[0]))

			if self.genSens_AdvMode == self.ADV_MODE_1:
				self.connTimeout = self.MAX_ADV_INTERVAL_MODE_1 + self.connTimeout_plus
				self.logger.info("[" + currentFuncName() + "] received: ADV_MODE_1")
			elif self.genSens_AdvMode == self.ADV_MODE_2:
				self.connTimeout = self.MAX_ADV_INTERVAL_MODE_2 + self.connTimeout_plus
				self.logger.info("[" + currentFuncName() + "] received: ADV_MODE_2")
			elif self.genSens_AdvMode == self.ADV_MODE_3:
				self.connTimeout = self.MAX_ADV_INTERVAL_MODE_3 + self.connTimeout_plus
				self.logger.info("[" + currentFuncName() + "] received: ADV_MODE_3")
			elif self.genSens_AdvMode == self.ADV_MODE_4:
				self.connTimeout = self.MAX_ADV_INTERVAL_MODE_4 + self.connTimeout_plus
				self.logger.info("[" + currentFuncName() + "] received: ADV_MODE_4")
			else:
				self.connTimeout = self.MAX_ADV_INTERVAL_MODE_4 + self.connTimeout_plus
				self.logger.warning("[" + currentFuncName() + "] received unexpected result: " + str(self.genSens_AdvMode))

			return self.genSens_AdvMode

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def set_genSens_AdvMode(self, advMode, **kwargs):
		try:
			assert (advMode >= self.ADV_MODE_1 and advMode <= self.ADV_MODE_4), ("Advertisement Mode has to be between 1 and 4")

			data = bytearray(uint8(advMode))

			await self.client.write_gatt_char(GenericSensor.GEN_SENS_ADV_MODE_CHAR_UUID, data, **kwargs)

			self.genSens_AdvMode = advMode
			if self.genSens_AdvMode == self.ADV_MODE_1:
				self.connTimeout = self.MAX_ADV_INTERVAL_MODE_1 + self.connTimeout_plus
				self.logger.info("[" + currentFuncName() + "] transmitted: ADV_MODE_1")
			elif self.genSens_AdvMode == self.ADV_MODE_2:
				self.connTimeout = self.MAX_ADV_INTERVAL_MODE_2 + self.connTimeout_plus
				self.logger.info("[" + currentFuncName() + "] transmitted: ADV_MODE_2")
			elif self.genSens_AdvMode == self.ADV_MODE_3:
				self.connTimeout = self.MAX_ADV_INTERVAL_MODE_3 + self.connTimeout_plus
				self.logger.info("[" + currentFuncName() + "] transmitted: ADV_MODE_3")
			elif self.genSens_AdvMode == self.ADV_MODE_4:
				self.connTimeout = self.MAX_ADV_INTERVAL_MODE_4 + self.connTimeout_plus
				self.logger.info("[" + currentFuncName() + "] transmitted: ADV_MODE_4")
			else:
				self.connTimeout = self.MAX_ADV_INTERVAL_MODE_4 + self.connTimeout_plus
				self.logger.warning("[" + currentFuncName() + "] transmitted unexpected value: " + str(self.genSens_AdvMode))

			return self.genSens_AdvMode

		except Exception as e:
			self.genSens_AdvMode = None
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_genSens_TxPwrLvl(self, **kwargs):
		if self.genSens_TxPwrLvl_AdvScan is not None:
			return self.genSens_TxPwrLvl_AdvScan, self.genSens_TxPwrLvl_Conn

		try:
			data = await self.client.read_gatt_char(GenericSensor.GEN_SENS_TX_PWR_LVL_CHAR_UUID, **kwargs)

			self.genSens_TxPwrLvl_AdvScan     = int(format(data[0]))
			self.genSens_TxPwrLvl_Conn        = int(format(data[1]))

			pwrLvl = ["TX_PWR_LVL_NEG_18_DBM",
					"TX_PWR_LVL_NEG_12_DBM",
					"TX_PWR_LVL_NEG_6_DBM",
					"TX_PWR_LVL_NEG_3_DBM",
					"TX_PWR_LVL_NEG_2_DBM",
					"TX_PWR_LVL_NEG_1_DBM",
					"TX_PWR_LVL_0_DBM",
					"TX_PWR_LVL_3_DBM",
					"TX_PWR_LVL_MAX"]

			self.logger.info("[" + currentFuncName() + "] received: "
				+ f"TxPwrLvl_AdvScan: {pwrLvl[self.genSens_TxPwrLvl_AdvScan-1]}\t"
				+ f"TxPwrLvl_Conn: {pwrLvl[self.genSens_TxPwrLvl_Conn-1]}")

			return self.genSens_TxPwrLvl_AdvScan, self.genSens_TxPwrLvl_Conn

		except Exception as e:
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def set_genSens_TxPwrLvl(self, advScan, conn, **kwargs):
		try:
			assert (advScan >= 1 and advScan <= 9), ("Parameter \'advScan\' has to be between 1 and 9")
			assert (conn >= 1 and conn <= 9), ("Parameter \'conn\' has to be between 1 and 9")

			data = bytearray(uint8(advScan), uint8(conn))

			self.client.write_gatt_char(GenericSensor.GEN_SENS_TX_PWR_LVL_CHAR_UUID, data, **kwargs)

			self.genSens_TxPwrLvl_AdvScan   = advScan
			self.genSens_TxPwrLvl_Conn      = conn

			pwrLvl = ["TX_PWR_LVL_NEG_18_DBM",
					"TX_PWR_LVL_NEG_12_DBM",
					"TX_PWR_LVL_NEG_6_DBM",
					"TX_PWR_LVL_NEG_3_DBM",
					"TX_PWR_LVL_NEG_2_DBM",
					"TX_PWR_LVL_NEG_1_DBM",
					"TX_PWR_LVL_0_DBM",
					"TX_PWR_LVL_3_DBM",
					"TX_PWR_LVL_MAX"]

			self.logger.info("[" + currentFuncName() + "] transmitted: "
				+ f"TxPwrLvl_AdvScan: {pwrLvl[self.genSens_TxPwrLvl_AdvScan-1]}\t"
				+ f"TxPwrLvl_Conn: {pwrLvl[self.genSens_TxPwrLvl_Conn-1]}")

			return self.genSens_TxPwrLvl_AdvScan, self.genSens_TxPwrLvl_Conn

		except Exception as e:
			self.genSens_TxPwrLvl_AdvScan = None
			self.genSens_TxPwrLvl_Conn = None
			self.logger.error("[" + currentFuncName() + "] received exception: " + str(e))
			raise e


	async def get_genSens(self, **kwargs):
		keepConnection = kwargs.get('keepConnection',None)
		kwargs['keepConnection'] = True
		try:
			await self.get_genSens_Label(**kwargs)
		except:
			pass
		try:
			await self.get_genSens_AdvMode(**kwargs)
		except:
			pass

		kwargs['keepConnection'] = keepConnection
		try:
			await self.get_genSens_TxPwrLvl(**kwargs)
		except:
			pass