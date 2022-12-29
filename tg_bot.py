from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, Update
import logging
from environs import Env
from quiz import get_quiz
from random import choice
from functools import partial
import redis


logger = logging.getLogger('quiz_boy_logger')


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    update.message.reply_text(ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True))


def help(bot, update):
    update.message.reply_text('Напиши /start, появятся кнопки, а там уже понятно)')


def handle_quiz_commands(bot, update, redis_db, quiz):
    user_id = update.effective_user.id
    if update.message.text == 'Новый вопрос':
        question = choice(list(quiz))
        redis_db.set(name=user_id, value=question)
        update.message.reply_text(question)
        return
    
    if update.message.text == 'Сдаться':
        return

    if update.message.text == 'Мой счёт':
        pass

    correct_answer = quiz.get(redis_db.get(user_id), "")
    if update.message.text.lower() == correct_answer.lower():
        update.message.reply_text('Правильно! Поздравляю!')
        return
    update.message.reply_text('Неправильно… Попробуешь ещё раз?')


    

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
        password=redis_password,
        decode_responses=True
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

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, quiz_handler))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
