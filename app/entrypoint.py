import logging
import os
import sys

from telegram2mqtt import Telegram2MQTT


def init_logging(level=logging.INFO):
    # Configure logging
    logging.basicConfig(
        stream=sys.stdout,
        format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
        level=level,
    )


if __name__ == "__main__":
    init_logging(level=logging.INFO)
    logging.debug(f"{os.environ.get('MQTT_BROKER_HOST') = }")
    logging.debug(f"{os.environ.get('BOT_TOKEN') = }")
    logging.debug(f"{os.environ.get('ALLOWED_TELEGRAM_IDS') = }")
    allowed_user_ids = [
        int(i) for i in os.environ.get("ALLOWED_TELEGRAM_IDS").split(",")
    ]
    logging.debug(f"{allowed_user_ids = }")
    t2m = Telegram2MQTT(
        os.environ.get("BOT_TOKEN"),
        os.environ.get("MQTT_BROKER_HOST"),
        allowed_user_ids,
    )
    t2m()
    logging.info("Telegram2MQTT is now offline.")
