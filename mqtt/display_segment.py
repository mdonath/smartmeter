#!/usr/bin/env python3

from Adafruit_LED_Backpack import SevenSegment
import paho.mqtt.client as mqtt
import time

#
#    0+     16+     48+     64+
#  .-0-.   .-0-.   .-0-.   .-0-.
#  5   1   5   1   5   1   5   1
#  >-6-<   >-6-<   >-6-<   >-6-<
#  4   2   4   2   4   2   4   2
#  *-3-*   *-3-*   *-3-*   *-3-*
#


ENERGY_TOPIC = "home/energy/power"
MQTT_HOST = "mqtt"


# global MqttDisplay
md = None


# MQTT callback
def on_message(client, userdata, message):
	global md
	md.display_payload(message)


class MqttDisplay(object):
	def __init__(self, callback, mqtthost=MQTT_HOST, topic=ENERGY_TOPIC):
		self.colon = True
		self.display = SevenSegment.SevenSegment()
		self.display.begin()
		self.display_started()

		self.mqttc = mqtt.Client("display_7segment")
		self.mqttc.on_message = callback
		self.mqttc.connect(mqtthost)
		self.mqttc.subscribe(topic)
		self.display_connected()


	def run_forever(self):
		self.mqttc.loop_forever()


	def display_payload(self, message):
		payload = str(message.payload.decode("utf-8"))
		if payload == '----':
			self.display_error()
		else:
			self.display.print_number_str(payload)
			self.colon = not self.colon
			self.display.set_left_colon(self.colon)
			self.display.write_display()


	def display_started(self):
		self.display_leds( [6, 16+6, 48+6, 64+6] )
	
	def display_connected(self):
		self.display_leds( [3,4,6, 16+2,16+3,16+4,16+6, 48+2,48+4,48+6, 64+2,64+4,64+6] )

	def display_error(self):
		self.display_leds([0,4,5,6,  16+0,16+1,16+2,16+3,16+4,16+5,  48+1,48+2,48+3,48+4,48+5, 64+3,64+4,64+5,64+6])

	def display_leds(self, leds):
		self.display.clear()
		for led in leds:
			self.display.set_led(led, True)
		self.display.write_display()
		time.sleep(1)

if __name__ == "__main__":
	md = MqttDisplay(on_message)
	md.run_forever()

