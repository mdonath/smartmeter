#!/usr/bin/env python3

from Adafruit_LED_Backpack import SevenSegment
import paho.mqtt.client as mqtt

ENERGY_TOPIC = "home/energy/power"
MQTT_HOST = "mqtt"

colon = True

def on_message(client, userdata, message):
	global colon
	payload = str(message.payload.decode("utf-8"))
	display.print_number_str(payload)
	colon = not colon
	display.set_left_colon(colon)
	display.write_display()

def display_started():
	display_leds( [6, 16+6, 48+6, 64+6] )
	
def display_connected():
	display_leds( [3,4,6, 16+2,16+3,16+4,16+6, 48+2,48+4,48+6, 64+2,64+4,64+6] )

def display_leds(leds):
	display.clear()
	for led in leds:
		display.set_led(led, True)
	display.write_display()




if __name__ == "__main__":
	display = SevenSegment.SevenSegment()
	display.begin()
	#display_started()

	mqttc = mqtt.Client("display_7segment")
	mqttc.on_message = on_message
	mqttc.connect(MQTT_HOST)
	mqttc.subscribe(ENERGY_TOPIC)
	display_connected()
	mqttc.loop_forever()

