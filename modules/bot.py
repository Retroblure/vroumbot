"""
Functionalities directly related to the bot.
"""
import datetime


from telegram import ForceReply, Update
from telegram.ext import CallbackContext, CommandHandler
from trello import TrelloClient


from secret import ADMIN_ID, TRELLO_API_KEY, TRELLO_API_SECRET, TRELLO_FEEDBACK_BOARD, TRELLO_FEEDBACK_LIST, TRELLO_LINK


from .base import Base


class Bot(Base):
    """
    Functionalities directly related to the bot.
    """

    MAX_FEEDBACKS = 10

    def __init__(self, logger=None):
        commandhandlers = [
            CommandHandler(["start", "hello", "hi"], self.start),
            CommandHandler(["help", "commands", "all_commands"], self.help_command),
            CommandHandler(["contribute", "github", "source", "git", "contrib"], self.contribute),
            CommandHandler(["feedback", "suggestion", "suggest"], self.feedback),
            CommandHandler(["feedbacks", "listfeedbacks"], self.feedbacks),
        ]
        super().__init__(logger, commandhandlers)

        self.__trello_client = TrelloClient(
            api_key=TRELLO_API_KEY,
            api_secret=TRELLO_API_SECRET,
        )

    def _access_feedback_list(self):
        """
        If properly configured, get the Trello feedbacks list.
        :return: trello.trellolist.List
        """
        try:
            board = None
            for board in self.__trello_client.list_boards():
                if board.name == TRELLO_FEEDBACK_BOARD:
                    break

            if not board:
                print("Trello is not configured properly: board not found.")
                return None

            liste = None
            for liste in board.list_lists():
                if liste.name == TRELLO_FEEDBACK_LIST:
                    break

            if not liste:
                print("Trello is not configured properly: list not found.")
                return None
        except:
            print("Trello is not configured properly: invalid credentials.")
            return None

        return liste

    def _add_feedback_to_trello(self, feedback):
        """
        Add a new feedback to the Trello feedbacks list.
        :param feedback: (title: String, description: String)
        :return: True if added successfully, else False.
        """
        liste = self._access_feedback_list()

        if liste:
            content, description = feedback
            liste.add_card(content, desc=description)
            return True

        return False

    def _get_feedbacks_from_trello(self):
        """
        Get the first `MAX_FEEDBACKS` the feedbacks from the Trello feedbacks list (titles only).
        :return: String if Trello active, else None.
        """
        liste = self._access_feedback_list()

        if liste:
            retour = []
            remaining = 0

            cards = liste.list_cards_iter()
            for i, card in enumerate(cards):
                retour.append("{}. {}".format(i + 1, card.name))
                if i == self.MAX_FEEDBACKS - 1:
                    break
            for _ in cards:
                remaining += 1
            if remaining > 0:
                retour.append("... And {} more!".format(remaining))

            return retour

    def start(self, update: Update, context: CallbackContext) -> None:
        """
        Says hello to the user and auto-enable the reply mode.
        """
        user = update.effective_user
        update.message.reply_markdown_v2(
            fr"Bonjour {user.mention_markdown_v2()} \!",
            reply_markup=ForceReply(selective=True),
        )

        self.logger.info("{} says hi!".format(user.first_name))

    def help_command(self, update: Update, context: CallbackContext) -> None:
        """
        Don't forget to update this manually.
        """

        text = "Available commands:\n"
        with open("./selected_commands", "r") as f:
            for line in f.readlines():
                text += "/{}".format(line)
        text += "\n... And more.\n"
        text += "All the commands and their descriptions are available here: https://github.com/Amustache/vroumbot/wiki/List-of-commands"

        update.message.reply_text(text, disable_web_page_preview=True)

        self.logger.info("{} wants to see all commands!".format(update.effective_user.first_name))

    def contribute(self, update: Update, context: CallbackContext) -> None:
        """
        To get the Git, basically.
        """
        update.message.reply_text(
            "Want to contribute? Use `/feedback <your proposition>` or go to https://github.com/Amustache/vroumbot!"
        )

        self.logger.info("{} wants to contribute!".format(update.effective_user.first_name))

    def feedback(self, update: Update, context: CallbackContext) -> None:
        """
        Get a written feedback, forward it to the admins groupchat or chat, and add it to Trello.
        """
        user = update.effective_user.first_name
        message_id = update.message.message_id
        chat_id = update.message.chat.id
        date = str(datetime.datetime.today())
        _, message = update.message.text.split(" ", 1)

        feedback = message, "Date: {}\nChat: {}\nMessage: {}\nUser: {}".format(
            date, chat_id, message_id, user
        )

        try:
            context.bot.sendMessage(chat_id=ADMIN_ID, text='{} says "{}"'.format(user, message))
        except:
            pass

        self._add_feedback_to_trello(feedback)

        self.logger.info("New feedback! {}".format(message))

    def feedbacks(self, update: Update, context: CallbackContext) -> None:
        """
        Send the first `MAX_FEEDBACKS` as a list to the user.
        """
        result = "List of first {} feedbacks:\n".format(self.MAX_FEEDBACKS)
        result += "\n".join(self._get_feedbacks_from_trello())
        result += "\n"
        result += TRELLO_LINK

        update.message.reply_text(result)

        self.logger.info("{} wants to know the feedbacks!".format(update.effective_user.first_name))
