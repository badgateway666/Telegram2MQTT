# T2M - Telegram2MQTT

Gateway for interacting with MQTT via Telegram.

## About
This project is in early-alpha stage.
You should definitely not use it for any kind of production environment.

T2M makes use of the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)  library
for interacting with telegram and [paho-mqtt](https://pypi.org/project/paho-mqtt/) as mqtt-client.

## HowTo

Currently, functionality is limited to the very basic mqtt operations:

- `/sub <topic>`              - Subscribe to mqtt topic `topic`
- `/unsub <topic>`            - Unsubcribe from mqtt topic `topic`
- `/pub <topic> <message>`    - Publish `message` on `topic`

A comma-separated list of allowed telegram-user-ids and the telegram bot token obtained by @botfather
are provided by environment variables.

A Dockerfile is provided for running and developing T2M with docker.
Additionally a docker-compose.yml with [mosquitto](https://mosquitto.org/) is included,
for having a full working environment upon starting with `docker-compose up`

For use with docker-compose,
it is advised to store your bot token in an environment-variable-file called `.env`
placed in the project's root directory.

## Not-working stuff
- Wildcard subs
- Re-subscribe between restarts

## Planned features
- Persistence of subscriptions between restarts
- Proper handling of wildcard topics
- `/help` commands with usage information
- Proper input validation
- Different message modes, f.e. binary data like photos as in- and output
- Better documentation
- Hook-Points for customizing gateway behavior
- Multi-User functionality
- ...