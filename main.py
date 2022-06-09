#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.
"""
Main! yay!
"""

import logging


from telegram.ext import Updater


from databases import User
from modules.bot import Bot
from modules.community.exp import Exp
from modules.community.karma import Karma
from modules.remindme import RemindMe
from modules.spam.media import Media
from modules.spam.privatejokes import PrivateJoke
from modules.spam.text import Text
from modules.special import Special
from secret import TOKEN


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it the bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Commands
    Bot(logger).add_commands(dispatcher)
    RemindMe(logger).add_commands(dispatcher)
    Special(logger).add_commands(dispatcher)

    # Community commands
    Exp(logger, table=User).add_commands(dispatcher)
    Karma(logger, table=User).add_commands(dispatcher)

    # Spam commands
    Media(logger).add_commands(dispatcher)
    PrivateJoke(logger).add_commands(dispatcher)
    Text(logger).add_commands(dispatcher)

    commands = ""
    for handler in dispatcher.handlers[0]:
        try:
            commands += "{}\n".format(
                "\n".join(
                    "{} - {}".format(command, handler.callback.__name__)
                    for command in handler.command
                )
            )
        except AttributeError:
            continue
    print("{}\nList of commands\n{}\n{}".format("*" * 13, commands, "*" * 13))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
