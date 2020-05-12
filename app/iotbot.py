import logging
import time
from queue import SimpleQueue
import paho.mqtt.client as mqtt
from telegram.bot import Bot as Telegram_Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


class IOTBot(object):
    """
    3 Threads:
        1. Control Thread for starting, stopping, retrieving and managing state.
        2. Telegram bot handler thread
        3. MQTT Client Thread

    2 Queues (evaluate!)
        1. Messages from Telegram to MQTT
        2. Messages from MQTT to Telegram

    """

    def __init__(self, bot_token, mqtt_broker_host, allowed_telegram_user_ids):
        self.telegram_bot = Telegram_Bot(bot_token)
        # self.updater = Updater(bot=self.bot)
        self.allowed_telegram_user_ids = allowed_telegram_user_ids

        # self.mqtt_client = mqtt.Client(client_id="IoT-Controller-Bot", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        # self.mqtt_client.connect(mqtt_broker_host, port=1883, keepalive=60, bind_address="")
        # self.topic = "asdf"
        # self.stop_signal = False

    def __call__(self):
        self.telegram_bot.send_message(743851810, "Huhu!")

    # def collect_mqtt_stuff(self):
    #     msg_info = self.mqtt_client.publish(self.topic, payload="Hello World!", qos=0, retain=False)
    #     msg_info.wait_for_publish()
    #     self.mqtt_client.subscribe(self.topic, qos=0)
    #     self.mqtt_client.on_message = self.mqtt_msg_callback
    #     self.mqtt_client.loop_start()  # start the loop
    #     while not self.stop_signal:
    #         time.sleep(2)
    #     self.mqtt_client.loop_stop()

    def mqtt_msg_callback(self, client, userdata, message):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

