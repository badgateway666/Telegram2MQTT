import logging
from queue import SimpleQueue

from telegram.bot import Bot as Telegram_Bot
from telegram.ext import Updater, CommandHandler, Filters


class TelegramHandler(object):
    def __init__(self, bot_token, allowed_telegram_user_ids):
        self.logger = logging.getLogger("telegram2mqtt.bot")

        self.telegram_bot = Telegram_Bot(bot_token)
        # self.telegram_bot.get_me()        # For debugging purposes
        self.allowed_telegram_user_ids = allowed_telegram_user_ids

        self.updater = Updater(bot=self.telegram_bot, use_context=True)
        self.topics_to_uid = {}
        self.sub_queue = SimpleQueue()
        self.unsub_queue = SimpleQueue()
        self.pub_queue = SimpleQueue()

        # Register Handlers
        self.updater.dispatcher.add_handler(
            CommandHandler(
                "sub",
                self.sub_handler,
                filters=Filters.user(self.allowed_telegram_user_ids),
            )
        )
        self.updater.dispatcher.add_handler(
            CommandHandler(
                "unsub",
                self.unsub_handler,
                filters=Filters.user(self.allowed_telegram_user_ids),
            )
        )
        self.updater.dispatcher.add_handler(
            CommandHandler(
                "pub",
                self.pub_handler,
                filters=Filters.user(self.allowed_telegram_user_ids),
            )
        )

        self.logger.info("Telegram-Handler is initialized.")

    def __call__(self):
        self.logger.info("Telegram-Handler started.")
        for uid in self.allowed_telegram_user_ids:
            self.telegram_bot.send_message(uid, "Telegram2MQTT Bot is online.")
        self.updater.start_polling()

    def stop(self):
        for uid in self.allowed_telegram_user_ids:
            self.telegram_bot.send_message(uid, "Telegram2MQTT Bot is offline.")
        self.logger.info("Telegram-Handler stopped.")
        self.updater.stop()

    def sub_handler(self, update, context):
        self.logger.debug(f"Sub Handler received args: '{context.args}'")
        # Validate context.args

        topic = context.args[0]
        if topic.count("#") >= 2:
            self.logger.warning(
                f"Invalid topic '{topic}' for subscription: Multiple '#' character used."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Invalid topic '{topic}' for subscription: Multiple '#' character used.",
            )
            return

        if "#" in topic and not topic.endswith("#"):
            self.logger.warning(
                f"Invalid topic '{topic}' for subscription: '#' not used as last character."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Invalid topic '{topic}' for subscription: '#' not used as last character.",
            )
            return

        if topic not in self.topics_to_uid:
            self.logger.info(f"Subscribe to topic '{topic}'")
            self.topics_to_uid[topic] = set()
            self.sub_queue.put(topic)

        if update.effective_chat.id not in self.topics_to_uid[topic]:
            self.topics_to_uid[topic].add(update.effective_chat.id)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Sub on topic '{topic}' received.",
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"It seems that you already subcribed to topic '{topic}'.",
            )

    def unsub_handler(self, update, context):
        self.logger.debug(f"Unsub Handler received args: '{context.args}'")
        # Validate context.args

        topic = context.args[0]
        if (
            topic not in self.topics_to_uid
            or update.effective_chat.id not in self.topics_to_uid[topic]
        ):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"It seems that you aren't subcribed on topic '{topic}'.",
            )
            return

        self.topics_to_uid[topic].remove(update.effective_chat.id)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Unsubcribed on topic '{topic}'."
        )
        if len(self.topics_to_uid[topic]) == 0:
            self.logger.info(f"Unsubscribe from topic '{topic}'")
            self.unsub_queue.put(topic)
            del self.topics_to_uid[topic]

    def pub_handler(self, update, context):
        topic, message = context.args[0], " ".join(context.args[1:])
        self.logger.info(
            f"Pub Handler received pub on topic '{topic}'. Message: '{message}'"
        )

        # Validate topic
        if "#" in topic or "+" in topic:
            self.logger.warning(
                f"Pub Handler received topic with wildcard-character: '{topic}'."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Invalid input: wildcard-character in topic '{topic}' detected.",
            )
            return

        # Validate msg, should empty messages be valid?

        self.pub_queue.put((topic, message))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Pub on topic '{topic}'.\nMessage: {message}",
        )

    def publish_to_telegram(self, topic, message):
        self.logger.debug(f"Message from MQTT. Topic: '{topic}' Message: '{message}'")
        if topic not in self.topics_to_uid:
            self.logger.error(
                f"Couldn't publish message '{message}' to topic '{topic}', no matching user id found."
            )
            return

        # TODO: Handle wildcards here
        # 1. Search for known subs to topics which match the mqtt messages topic
        # 2. Collect all users which subbed to any of these topics
        # 3. Store as set to deduplicate, and forward message

        self.logger.info("Forwarding mqtt-message to telegram.")
        telegram_msg = f"Received message on topic '{topic}':\n{message}"
        for uid in self.topics_to_uid[topic]:
            self.telegram_bot.send_message(uid, telegram_msg)

    @staticmethod
    def make_regex_from_topic(topic):
        """
        For subscriptions, two wildcard characters are supported:
            - A '#' character represents a complete sub-tree of the hierarchy
                and thus must be the last character in a subscription topic string, such as SENSOR/#.
                This will match any topic starting with SENSOR/, such as SENSOR/1/TEMP and SENSOR/2/HUMIDITY.
            - A '+' character represents a single level of the hierarchy and is used between delimiters.
                For example, SENSOR/+/TEMP will match SENSOR/1/TEMP and SENSOR/2/TEMP.

        """
        pass
