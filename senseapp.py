#!/usr/bin/python3

from senseapp import config
from senseapp.system import System
from senseapp.sense_hat import SenseHat
from senseapp.thermostat import Thermostat
from senseapp.api import API

import time

import subprocess

class SenseApp:

    settings_manager = None
    system_manager = None
    sense_hat = None
    api = None

    def __init__(self):
        self.settings_manager = config.Manager()
        self.settings_manager.on_update(self.settings_updated)
        self.system_manager = System()
        self.sense = SenseHat(self.settings_manager)
        self.api = API(self)

        self.api.connect()

        print(self.settings_manager.get_all())
        print(self.system_manager.info())
        print(self.sense.get_sensor_values())
        print('still alive')

        # self.sense.display("*** SenseApp ***")

    def get_ip(self):
        ip = subprocess.getoutput("ip -4 addr | grep -oP '(?<=inet\s)\d+(\.\d+){3}'")
        if ip=="127.0.0.1":
            return "NO IP!"
        else:
            return ip.replace("127.0.0.1\n", "").replace("\n", " | ")

    def print_ip(self):
        ip = self.get_ip()
        print("IP: {}".format(ip))
        screen_output = ip + " - " + ip + " - " + ip
        self.sense.display(screen_output, color=[255,98,1])

    def run(self):
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


if __name__ == "__main__":
    # sleep for 5 sec to let DHCP finish first before requesting the ip
    time.sleep(5.0)
    app = SenseApp()
    app.print_ip()
    app.run()