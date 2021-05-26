#!/usr/bin/python3

from senseapp import config
from senseapp.sense_hat import SenseHat
from senseapp.thermostat import Thermostat
from senseapp.api import API

import socket
import time

class SenseApp:

    settings_manager = None
    sense_hat = None
    api = None

    def __init__(self):
        self.settings_manager = config.Manager()
        self.settings_manager.on_update(self.settings_updated)
        self.sense = SenseHat(self.settings_manager)
        self.api = API(self)
        

        self.api.connect()

        print(self.settings_manager.get_all())
        print(self.sense.get_sensor_values())
        print('still alive')

        # self.sense.display("*** SenseApp ***")

    def run(self):
        self.displayIp()
        while True:
            self.update_sensors()
            time.sleep(1.0)

    def print_sensor_values(self, sensor_values):
        print("Pressure:    %s Millibars" % "{:2.1f}".format(sensor_values["pressure"]))
        print("Temperature: %s C" % "{:2.1f}".format(sensor_values["temperature"]))
        print("Humidity:    %s %%rH" % "{:2.1f}".format(sensor_values["humidity"]))

    def update_sensors(self):
        sensor_values = self.sense.get_sensor_values()
        self.print_sensor_values(sensor_values)
        self.api.update_sensor_values(sensor_values)

        temperature = sensor_values["temperature"]

        thermostat = Thermostat(
            self.settings_manager.get("wanted_temperature"),
            self.settings_manager.get("wanted_temperature_range")
            )
        thermostat.update(temperature)
        
        color= [0, 255, 0]
        if thermostat.is_heating():
            color = [0, 0, 255]
        elif thermostat.is_cooling():
            color = [255, 0, 0]
        
        self.display_temperature(temperature, color)
        
    def display_temperature(self, temperature, color):
        temperature_string ="{:2.1f}C".format(temperature)
        self.sense.display(temperature_string, color=color)

    def settings_updated(self, setting, value):
        # print(f"settings update: {setting}: {value}")
        if setting == "low_light":
            self.sense.update_low_light(value)
        elif setting == "rotation":
            self.sense.update_rotation(value)


    def getIp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP


    def displayIp(self):
        counter = 6
        while counter > 0:
            self.sense.display(self.getIp(), color=[0, 255, 0])
            time.sleep(1.0)
            counter-=1


if __name__ == "__main__":
    app = SenseApp()
    app.run()