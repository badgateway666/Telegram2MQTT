import logging
import time
from queue import SimpleQueue

import paho.mqtt.client as mqtt


class MQTTHandler(object):
    def __init__(self, mqtt_broker_host, mqtt_broker_port=1883):
        self.logger = logging.getLogger("mqtt.client")
        self.mqtt_broker_host = mqtt_broker_host
        self.mqtt_broker_port = mqtt_broker_port
        self.mqtt_client = mqtt.Client(
            client_id="telegram2mqtt", protocol=mqtt.MQTTv311, transport="tcp"
        )
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message
        self.pending_messages = SimpleQueue()
        self.connected = False
        self.logger.info("MQTT-Handler is initialized.")

    def __call__(self):
        self.mqtt_client.connect_async(self.mqtt_broker_host, port=1883)
        self.mqtt_client.loop_start()
        self.logger.info("MQTT-Client started.")

    def on_connect(self, client, userdata, flags, rc):
        self.logger.debug(f"MQTT-Client connected. Flags: {flags}. Result code {rc}")
        self.connected = True

    def on_disconnect(self, client, userdata, rc):
        self.logger.debug(f"MQTT-Client disconnected. Result code {rc}")

    def on_message(self, client, userdata, msg):
        self.logger.debug(
            f"MQTT-Client received mesage. Topic: '{msg.topic}'  Message: '{msg.payload}'"
        )
        self.pending_messages.put((msg.topic, msg.payload))

    def subscribe(self, topic):
        while not self.connected:
            self.logger.debug("Subscribe - wait for connect...")
            time.sleep(0.5)
        self.mqtt_client.subscribe(topic)
        self.logger.debug(f"Subscribed to {topic}")

    def unsubscribe(self, topic):
        while not self.connected:
            self.logger.debug("Unsubscribe - wait for connect...")
            time.sleep(0.5)
        self.mqtt_client.unsubscribe(topic)
        self.logger.debug(f"Unsubscribed from {topic}")

    def publish(self, topic, message):
        while not self.connected:
            self.logger.debug("Publish - wait for connect...")
            time.sleep(0.5)
        self.mqtt_client.publish(topic, payload=message)
        self.logger.debug(f"Published message '{message}' on topic '{topic}'.")

    def disconnect(self):
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()
        self.logger.info("MQTT-Client stopped.")
