import logging


class LoggerHandler(logging.Handler):

    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        entry = self.format(record)
        self.bot.send_message(self.chat_id, text=entry)