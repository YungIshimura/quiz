from environs import Env
import random

import redis
import vk_api as vk

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from quiz import get_quiz


def start_quiz(vk_api, redis_db, user_id):
    keyboard = VkKeyboard()
    keyboard.add_button(
        'Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)
    vk_api.messages.send(
        user_id=user_id,
        message='О, там внизу кнопки!',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )
    user_key = f'{user_id}_quiz_started'
    redis_db.set(user_key, 1)


def ask_question(vk_api, redis_db, user_id, quiz):
    question = random.choice(list(quiz.keys()))
    redis_db.set(name=user_id, value=question)
    vk_api.messages.send(
        user_id=user_id,
        message=question,
        random_id=random.randint(1, 1000),
    )


def get_answer(vk_api, redis_db, user_id, quiz):
    correct_answer = quiz.get(redis_db.get(user_id), "")
    vk_api.messages.send(
        user_id=user_id,
        message=f'Правильный ответ:\n{correct_answer}',
        random_id=random.randint(1, 1000),
    )


def check_answer(vk_api, redis_db, user_id, quiz):
    correct_answer = quiz.get(redis_db.get(user_id), "")
    if event.text.lower() == correct_answer.lower():
        vk_api.messages.send(
            user_id=user_id,
            message='Правильно! Поздравляю!',
            random_id=random.randint(1, 1000),
        )
        return
    vk_api.messages.send(
        user_id=user_id,
        message='Неправильно… Попробуешь ещё раз?',
        random_id=random.randint(1, 1000),
    )


if __name__ == "__main__":
    env = Env()
    env.read_env()
    redis_host = env("REDIS_DB_HOST")
    redis_port = env("REDIS_DB_PORT")
    redis_password = env("REDIS_DB_PASSWORD")
    redis_db = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True,
    )
    quiz = get_quiz('quiz_items')

    vk_token = env("VK_API_KEY")
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            if event.text == "Квиз":
                start_quiz(vk_api, redis_db, user_id)
            elif event.text == 'Новый вопрос':
                ask_question(vk_api, redis_db, user_id, quiz)
            elif event.text == 'Сдаться':
                get_answer(vk_api, redis_db, user_id, quiz)
            else:
                check_answer(vk_api, redis_db, user_id, quiz)
