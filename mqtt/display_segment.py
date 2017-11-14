#!/usr/bin/env python3

from Adafruit_LED_Backpack import SevenSegment
import paho.mqtt.client as mqtt
import time, datetime

#
#    0+     16+     48+     64+
#  .-0-.   .-0-.   .-0-.   .-0-.
#  5   1   5   1   5   1   5   1
#  >-6-<   >-6-<   >-6-<   >-6-<
#  4   2   4   2   4   2   4   2
#  *-3-*   *-3-*   *-3-*   *-3-*
#
#    01
#  32  02
#    64
#  16  04
#    08

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
		self.display.set_brightness(1)

		self.mqttc = mqtt.Client("display_7segment")
		self.mqttc.on_message = callback
		self.mqttc.connect(mqtthost)
		self.mqttc.subscribe(topic)
		self.display_connected()

		self.showMQTT = False
		self.showTime = True


	def run_forever(self):
		# self.mqttc.loop_forever()
		self.mqttc.loop_start()


	def display_payload(self, message):
		payload = str(message.payload.decode("utf-8"))
		self.display_string(payload)

	def display_string(self, payload):
		if payload == '----':
			self.display_error()
		elif self.showTime == True:
			self.showTime = True
			self.display.set_left_colon(False)

			now = datetime.datetime.now()
			hour = now.hour
			minute = now.minute
			second = now.second

			self.display.clear()
			# Set hours
			self.display.set_digit(0, int(hour / 10))     # Tens
			self.display.set_digit(1, hour % 10)          # Ones
			# Set minutes
			self.display.set_digit(2, int(minute / 10))   # Tens
			self.display.set_digit(3, minute % 10)        # Ones
			# Toggle colon
			self.display.set_colon(second % 2)            # Toggle colon at 1Hz
			
			# Write the display buffer to the hardware.  This must be called to
			# update the actual display LEDs.
			self.display.write_display()

		elif self.showMQTT:
			self.display.clear()
			self.display.print_float(float(payload), decimal_digits=3, justify_right=False)
			self.colon = not self.colon
			self.display.set_colon(False)
			self.display.set_left_colon(self.colon)
			self.display.write_display()

		else:
			self.display_leds_mask( [83,83,83,83] )

#       01(0)
#  32(5)     02(1)
#       64(6)
#  16(4)     04(2)
#       08(3)

	def display_started(self):
		self.display_leds_mask( [64,64,64,64] )
	
	def display_connected(self):
		self.display_leds_mask( [88,92,84,84] )

	def display_error(self):
		self.display_leds([0,4,5,6,  16+0,16+1,16+2,16+3,16+4,16+5,  48+1,48+2,48+3,48+4,48+5, 64+3,64+4,64+5,64+6])

	def display_leds_mask(self, leds):
		self.display.clear()
		for i, mask in enumerate(leds):
			self.display.set_digit_raw(i,mask)
		self.display.write_display()
		time.sleep(1)
	
	def display_leds(self, leds):
		self.display.clear()
		for led in leds:
			self.display.set_led(led, True)
		self.display.write_display()
		time.sleep(1)

if __name__ == "__main__":
	md = MqttDisplay(on_message)
	md.run_forever()
	print("loop started")
	while True:
		time.sleep(3 if md.showTime else 10)
		md.showTime = not md.showTime
		md.showMQTT = not md.showMQTT

