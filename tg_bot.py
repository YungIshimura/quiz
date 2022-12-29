from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import logging
from environs import Env
from quiz import get_quiz
from random import choice


logger = logging.getLogger('quiz_boy_logger')


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.effective_chat.id,
                     text="О, там внизу кнопки",
                     reply_markup=reply_markup,)


def help(bot, update):
    update.message.reply_text('Help!')


def send_question(bot, update):
    if update.message.text == 'Новый вопрос':
        quiz = get_quiz('quiz_items')
        question = choice(list(quiz))
        update.message.reply_text(question)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    env = Env()
    env.read_env()
    tg_token = env('TG_API_KEY')

    """Start the bot."""

    updater = Updater(tg_token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.text, send_question))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
