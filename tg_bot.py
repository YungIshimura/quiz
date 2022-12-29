from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import logging
from environs import Env
from quiz import get_quiz
from random import choice
from functools import partial
import redis


logger = logging.getLogger('quiz_boy_logger')


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.effective_chat.id,
                     text="О, там внизу кнопки",
                     reply_markup=reply_markup,)


def help(bot, update):
    update.message.reply_text('Help!')


def handle_quiz_commands(bot, update, redis_db, quiz):
    if update.message.text == 'Новый вопрос':
        question = choice(list(quiz))
        redis_db.set(name=update.effective_user.id, value=question)
        update.message.reply_text(question)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    env = Env()
    env.read_env()
    tg_token = env('TG_API_KEY')
    redis_host = env("REDIS_DB_HOST")
    redis_port = env("REDIS_DB_PORT")
    redis_password = env("REDIS_DB_PASSWORD")

    bot_redis_db = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password
    )

    quiz = quiz = get_quiz('quiz_items')

    quiz_handler = partial(
        handle_quiz_commands,
        redis_db=bot_redis_db,
        quiz=quiz
    )
    
    updater = Updater(tg_token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.text, quiz_handler))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
