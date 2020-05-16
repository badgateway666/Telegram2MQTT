import logging
import signal
import threading
import time

from mqtt_handler import MQTTHandler
from telegram_handler import TelegramHandler


class SIGTERMHandler:
    """
    SIGTERMHandler

    Sets flag upon receiving SIGINT or SIGTERM (like from 'docker stop')
    """
    def __init__(self):
        self.sigterm_received = False
        signal.signal(signal.SIGINT, self.receive_sigterm)
        signal.signal(signal.SIGTERM, self.receive_sigterm)

    def receive_sigterm(self, signum, frame):
        logging.debug("Signal received")
        self.sigterm_received = True


class Telegram2MQTT(object):
    """
    Telegram2MQTT-Gateway Bot


    """

    def __init__(self, bot_token, mqtt_broker_host, allowed_telegram_user_ids):
        self.logger = logging.getLogger("telegram2mqtt")
        # Initialize mqtt-client
        self.mqtt_handler = MQTTHandler(mqtt_broker_host)

        # Initialize telegram-bot
        self.telegram_handler = TelegramHandler(bot_token, allowed_telegram_user_ids)
        self.telegram_thread = threading.Thread(target=self.telegram_handler)

    def __call__(self):
        """
        'Main'-Method
        """
        self.mqtt_handler()                 # Start mqtt client
        self.telegram_thread.start()        # Start telegram bot
        s = SIGTERMHandler()
        self.logger.info("Starting main loop.")
        while not s.sigterm_received:
            action_done = False

            if not self.mqtt_handler.pending_messages.empty():
                self.logger.debug("Handling mqtt message from queue.")
                topic, message = self.mqtt_handler.pending_messages.get()
                self.telegram_handler.publish_to_telegram(topic, message)
                action_done = True

            if not self.telegram_handler.sub_queue.empty():
                self.logger.debug("Handling sub from queue.")
                topic = self.telegram_handler.sub_queue.get()
                self.mqtt_handler.subscribe(topic)
                action_done = True

            if not self.telegram_handler.unsub_queue.empty():
                self.logger.debug("Handling unsub from queue.")
                topic = self.telegram_handler.unsub_queue.get()
                self.mqtt_handler.unsubscribe(topic)
                action_done = True

            if not self.telegram_handler.pub_queue.empty():
                self.logger.debug("Handling pub from queue.")
                topic, message = self.telegram_handler.pub_queue.get()
                self.mqtt_handler.publish(topic, message)
                action_done = True

            if not action_done:
                time.sleep(0.1)

        self.logger.info("Shutting down Telegram2MQTT")
        self.mqtt_handler.disconnect()
        self.telegram_handler.updater.stop()
        self.telegram_thread.join()
