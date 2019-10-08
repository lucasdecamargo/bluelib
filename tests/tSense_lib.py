# ------------------------------------------------------------------------------#
# --------------------------------CLASS TMRTF-----------------------------------#
# -Description:                                                                -#
# --The class sensor describes one BLE sensor. To create a sensor, you need to--#
# --call the __init__ function with the parameters from the whitelist.dat.    --#
# --Afterwards you can connect,  measure the temperature or measure the       --#
# --battery status and also disconnect from the BLE device. Don't forget to   --#
# --disconnect at the end!                                                    --#
# ------------------------------------------------------------------------------#
# -History:                                                                    -#
# --20.06.2018(jtz_sk): Added function to get sensor type from sensor         --#
# --22.03.2018(jtz_sk): deleted the name parameter in constructor             --#
# --21.03.2018(jtz_sk): cleaned up and reorganized the code a little bit      --#
# --25.06.2018(jtz): Trigger value type changed to np.uint8                   --#
# --24.07.2018(jtz): Completely new                                           --#
# --25.09.2018(jtz): Discrimination between receive_"value" from sensor       --#
#                    and get_"value" from variable                            --#
#                    resp. transmit_"value" and set_"value"                   --#
# --02.01.2019(sdr): maxretries as optional variable at object creation       --#
# --??.??.2019(jtz_rm): additional functions for use with temperaturesystem   --#
# --06.02.2019(sdr): consolidation of different library versions to git       --#
# --03.04.2019(sdr_js): redesign for windows and linux usage (basic functions)--#
# --Sensor software has to be upgrade for functionality                       --#
# --11.06.2019(sdr_js): Get all functions working + retries, when no connect  --#
# --18.07.2019(dhl_lc): Rewrote class to improve perfomance and debugging     --#
# ------------------------------------------------------------------------------#

from sensorlib.blesensor import *
import asyncio
import logging
import logging.handlers


class tSense(GenericSensor, DeviceInformation, Temperature, Battery):

    def __init__(self, address, loop=None, **kwargs):
        super().__init__(address, loop, **kwargs)

        self.__first_connection__ = False


    async def connect(self, **kwargs):
        try:
            if self.__first_connection__ is False:
                self.__first_connection__ = True
                await GenericSensor.connect(self,**kwargs)
                return await self.get_device_parameters(keepConnection=True, **kwargs)
            else:
                return await GenericSensor.connect(self,**kwargs)
        except Exception as e:
            raise e


    async def get_device_parameters(self, keepConnection=None, **kwargs):
        try:
            await self.get_genAcc_DeviceName(keepConnection=True, **kwargs)
        except:
            pass

        await self.get_devInf(keepConnection=True, **kwargs)
        await self.get_genSens(keepConnection=True, **kwargs)

        try:
            await self.get_temp_CalibrationData(keepConnection=keepConnection, **kwargs)
        except:
            pass


    async def measure(self, values: list) -> list:
        assert (values is not None and len(values) > 0), ("[tSense.measure] values has to be a valid list of strings")

        await self.connect()

        ret_val = []
        for v in values:
            if v.lower() == "temperature":
                for i in range(0,3):
                    try:
                        result = await self.get_temp_Temperature(keepConnection=True)
                        ret_val.append(float(result))
                        break
                    except:
                        pass

            elif v.lower() == "battery":
                for i in range(0,3):
                    try:
                        result = await self.get_battery_BatteryLevel(keepConnection=True)
                        ret_val.append(float(result))
                        break
                    except:
                        pass

        await self.disconnect()

        assert (len(ret_val) > 0), ("[tSense.measure] no valid value was found")

        return ret_val




# -------- FOR TESTS PURPOUSES -------- #
async def main(loop):
    import time

    sensor = tSense("57:5a:4c:a2:e8:ac", loop=loop, defaultKeepConnection=False)

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

    await sensor.connect(retries=1)
    await asyncio.sleep(2,loop=loop)
    await sensor.client.disconnect()



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))