from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, Update
import logging
from environs import Env
from quiz import get_quiz
from random import choice
from functools import partial
import redis


QUESTION, ANSWER = range(2)


def start(bot, update):
    reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    update.message.reply_text('Привет, там внизу кнопки!',
                              reply_markup=ReplyKeyboardMarkup(
                                  reply_keyboard, resize_keyboard=True))

    return QUESTION


def handle_new_question_request(bot, update, redis_db, quiz):
    user_id = update.effective_user.id
    question = choice(list(quiz.keys()))
    redis_db.set(name=user_id, value=question)
    update.message.reply_text(question)
    return ANSWER


def handle_solution_attempt(bot, update, redis_db, quiz):
    user_id = update.effective_user.id
    correct_answer = quiz.get(redis_db.get(user_id), "")
    if update.message.text.lower() == correct_answer.lower():
        update.message.reply_text('Правильно! Поздравляю!')

        return QUESTION
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')

        return ANSWER


def done(update, context):

    user_data = context.user_data

    update.message.reply_text(
        'Возвращайтесь еще!',
    )

    user_data.clear()
    return ConversationHandler.END


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

    question_request = partial(
        handle_new_question_request,
        redis_db=bot_redis_db,
        quiz=quiz
    )
    solution_attempt = partial(
        handle_solution_attempt,
        bot_db=bot_redis_db,
        quiz=quiz,
    )
    updater = Updater(tg_token)

    dp = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUESTION: [
                MessageHandler(Filters.regex('^Новый вопрос$'), question_request)
            ],
            ANSWER: [
                MessageHandler(Filters.text, solution_attempt),
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    dp.add_handler(conversation_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
