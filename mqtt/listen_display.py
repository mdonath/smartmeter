#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from Adafruit_LED_Backpack import SevenSegment
import paho.mqtt.client as mqtt


LED_TOPIC = "home/sevensegment/display"


def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	print("Received message: " + msg)
	if ":" in msg:
		display.set_colon(True)
		display.set_left_colon(False)
		display.set_fixed_decimal(False)
		msg = msg[:2] + msg[-2:]
		display.print_number_str(msg)
	elif "°C" in msg:
		display.set_colon(True)
		display.set_left_colon(False)
		display.set_fixed_decimal(True)
		temp = msg[:2] + msg[3:4] + "C"
		display.print_number_str(temp)
	elif msg.startswith("txt{"):
		display.set_colon(False)
		display.set_left_colon(False)
		display.print_number_str(msg[4:8])
	else:
		display.set_colon(False)
		display.set_left_colon(False)
		display.print_number_str(msg)
	try:
		display.write_display()
	except:
		print("Fout opgetreden")


if __name__ == '__main__':
	mqttc = mqtt.Client("7segment-display")
	mqttc.on_message = on_message
	mqttc.connect("mqtt")
	mqttc.subscribe(LED_TOPIC)

	display = SevenSegment.SevenSegment()
	display.begin()
	display.set_brightness(1)
	display.print_number_str("----")
	display.write_display()

	mqttc.loop_forever()
