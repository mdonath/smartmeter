#!/usr/bin/env python3

import re
import sys
import serial
import paho.mqtt.client as mqtt
import time

# I found this class somewhere on the internet and cannot find the source.
# So... Kudos to whoever made this.
# I modified it slightly for my own situation.

MQTT_HOST = "mqtt"

class P1Sensor(object):
	"""
	"""

	def __init__(self):
		self.initialized = False
		self.serial = serial.Serial()

	def init_connection(self):
		"""
		Connects to the serial port.
		"""
		self.serial.baudrate = 115200
		self.serial.bytesize = serial.EIGHTBITS
		self.serial.parity = serial.PARITY_NONE
		self.serial.stopbits = serial.STOPBITS_ONE
		self.serial.xonxoff = 1
		self.serial.rtscts = 0
		self.serial.timeout = 20
		self.serial.port = "/dev/ttyUSB0"

		try:
			self.serial.open()
		except:
			print("Error opening serial connection")
			sys.exit(1)

		self.initialized = True

	def read_data(self):
		"""
		Reads data from the serial port.
		"""
		if not self.initialized:
			self.init_connection()

		try:
			raw_data = self.serial.readline()
		except KeyboardInterrupt:
			self.serial.close()
			sys.exit(0)
		except:
			self.serial.close()
			print("Error reading data from serial connection")
			sys.exit(1)

		return str(raw_data, "utf-8").strip()


class MqttEnergyClient(object):
	def __init__(self, host):
		self.mqttc = mqtt.Client()
		self.mqttc.connect(host)
		self.mqttc.loop_start()

	def parse_and_publish_power(self, data):
		self.parse_and_publish(data, "home/energy/power", r"1\-0:1\.7\.0\(([0-9\.]+)\*kW\)")

	def parse_and_publish_gas(self, data):
		self.parse_and_publish(data, "home/energy/gas", r"0\-1:24\.2\.1\([0-9]{12}S\)\((.+)\*m3\)")

	def parse_and_publish(self, data, topic, regexp):
		match = re.match(regexp, data)
		if match is not None:
			value = "{:0.3f}".format(float(match.group(1)))
			self.mqttc.publish(topic, value)


if __name__ == "__main__":
	p1sensor = P1Sensor()

	mqtt = MqttEnergyClient(MQTT_HOST)

	while True:
		data = p1sensor.read_data()
		mqtt.parse_and_publish_power(data)
		mqtt.parse_and_publish_gas(data)

