import logging
import os
import time as tm
from datetime import datetime
from typing import List

import telebot
from telebot import types

from app.database.db import session
from app.database.models import Features
from app.Resources import phrases_kz, phrases_ru
from app.telegrah_helper import create_telegraph, create_telegraph_for_all_crimes
from app.yandex_helper import generate_and_send_stat_map_jpg, generate_maps_pins_url

from app.utils import (  # isort:skip
    get_user_lang,
    get_user_set_radius,
    message_counter,
    get_crime_codes,
    set_radius,
    user_create,
    set_lang_user,
    get_user_action,
    set_geo_user,
    set_user_action,
    haversine,
)


logger = logging.getLogger(__name__)
TOKEN = os.getenv("BOT_API_TOKEN")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "/start":
        handle_start(message)

    elif message.text == "/crimes":
        crimes(message)

    elif message.text == "/set_points":
        get_user_lang(message.chat.id)

    elif message.text == "/last_20":
        handle_last_20(message)

    else:

        bot.lang = get_user_lang(message.chat.id)
        if bot.lang == "ru":
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(
                text=phrases_ru.COMMANDS, callback_data="commands-ru"
            )
            string_to_send = phrases_ru.UNKNOWN_COMMANDS
            markup.add(button)
            bot.send_message(message.chat.id, string_to_send, reply_markup=markup)

        elif bot.lang == "kz":
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(
                text=phrases_kz.COMMANDS, callback_data="commands-kz"
            )
            string_to_send = phrases_kz.UNKNOWN_COMMANDS
            markup.add(button)
            bot.send_message(message.chat.id, string_to_send, reply_markup=markup)


def handle_loc(message):
    lang = get_user_lang(message.chat.id)

    keyboard = types.ReplyKeyboardMarkup(
        one_time_keyboard=True, row_width=1, resize_keyboard=True
    )
    notificate = "error 404"

    if lang == "ru":
        button_location = types.KeyboardButton(
            text=phrases_ru.SEND_GEO, request_location=True
        )
        notificate = phrases_ru.ONCLICK_LOCATION_BUTTON
        keyboard.add(button_location)

    elif lang == "kz":
        button_location = types.KeyboardButton(
            text=phrases_kz.SEND_GEO, request_location=True
        )
        notificate = phrases_kz.ONCLICK_LOCATION_BUTTON
        keyboard.add(button_location)

    message_counter(message.chat.id)
    bot.send_message(message.chat.id, notificate, reply_markup=keyboard)


@bot.message_handler(commands=["start"])
def handle_start(message):
    status: bool = user_create(
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        tg_id=message.chat.id,
    )
    message_counter(message.chat.id)
    lang = get_user_lang(message.chat.id)

    if lang is None:
        choose_lang(message)

    else:
        bot.lang = lang

        if bot.lang == "ru":
            welcome_message = phrases_ru.WELCOME
            markup = types.InlineKeyboardMarkup()
            keyboard_button = types.InlineKeyboardButton(
                text=phrases_ru.COMMANDS, callback_data="commands-ru"
            )
            markup.add(keyboard_button)
            bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

        elif bot.lang == "kz":
            welcome_message = phrases_kz.WELCOME
            markup = types.InlineKeyboardMarkup()
            keyboard_button = types.InlineKeyboardButton(
                text=phrases_kz.COMMANDS, callback_data="commands-kz"
            )
            markup.add(keyboard_button)
            bot.send_message(message.chat.id, welcome_message, reply_markup=markup)


def choose_lang(message):
    markup = types.InlineKeyboardMarkup()
    keyboard_button_ru = types.InlineKeyboardButton(
        text=phrases_ru.LANG, callback_data="ru"
    )
    keyboard_button_kz = types.InlineKeyboardButton(
        text=phrases_kz.LANG, callback_data="kz"
    )

    markup.add(keyboard_button_ru)
    markup.add(keyboard_button_kz)

    bot.send_message(
        message.chat.id,
        f"{phrases_ru.CHOOSE_LANG} \n{phrases_kz.CHOOSE_LANG} \n\n",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda message: True)
def handle_query(message):
    if message.data == "/last_20":
        handle_last_20(message.message)

    if message.data.split("-")[0] == "commands":
        if message.data.split("-")[1] == "ru":
            bot.lang = "ru"
            message_send = commands_list(bot.lang)

            bot.send_message(
                message.message.chat.id,
                message_send["str_to_send"],
                reply_markup=message_send["keyboard"],
            )
            message_counter(message.message.chat.id)

        elif message.data.split("-")[1] == "kz":
            bot.lang = "kz"
            message_send = commands_list(bot.lang)

            bot.send_message(
                message.message.chat.id,
                message_send["str_to_send"],
                reply_markup=message_send["keyboard"],
            )
            message_counter(message.message.chat.id)

    elif message.data == "/crimes":
        bot.lang = get_user_lang(message.message.chat.id)
        message_counter(message.message.chat.id)

        set_radius_b(bot.lang, message.message, bot)

    elif message.data == "ru":
        message_counter(message.message.chat.id)
        set_lang_user(tg_id=message.message.chat.id, lang="ru")

        bot.lang = "ru"
        handle_start(message.message)

    elif message.data == "kz":
        message_counter(message.message.chat.id)
        set_lang_user(tg_id=message.message.chat.id, lang="kz")

        bot.lang = "kz"
        handle_start(message.message)


def set_radius_b(lang, message, bot):
    to_user_send_str = ""
    if lang == "ru":
        to_user_send_str += phrases_ru.RADIUS_SET

    elif lang == "kz":
        to_user_send_str += phrases_kz.RADIUS_SET

    bot.send_message(message.chat.id, to_user_send_str)
    bot.register_next_step_handler(message, handle_setting_radius)


def handle_setting_radius(message):
    try:
        float(message.text)
        lang = get_user_lang(message.chat.id)
        set_radius(tg_id=message.chat.id, radius=message.text)

        crimes(message, lang)

    except ValueError:
        lang = get_user_lang(message.chat.id)
        if lang == "ru":
            bot.send_message(message.chat.id, phrases_ru.RADIUS_IN_NUMS)
            set_radius_b(lang, message, bot)

        elif lang == "kz":
            bot.send_message(message.chat.id, phrases_kz.RADIUS_IN_NUMS)
            set_radius_b(lang, message, bot)


def commands_list(lang):
    str_to_send = "ERROR"
    markup = "ERROR"

    if lang == "ru":
        markup = types.InlineKeyboardMarkup()
        commands_list_ = [
            [phrases_ru.COMMAND_REQUEST_CRIMES_NEAR_ME, "/crimes"],
            [phrases_ru.COMMAND_REQUEST_LAST_CRIMES, "/last_20"],
        ]
        str_to_send = phrases_ru.WHAT_I_CAN

        for key, command in enumerate(commands_list_):
            markup.add(
                types.InlineKeyboardButton(text=command[0], callback_data=command[1])
            )

    elif lang == "kz":
        markup = types.InlineKeyboardMarkup()
        commands_list_ = [
            [phrases_kz.COMMAND_REQUEST_CRIMES_NEAR_ME, "/crimes"],
            [phrases_kz.COMMAND_REQUEST_LAST_CRIMES, "/last_20"],
        ]
        str_to_send = phrases_kz.WHAT_I_CAN

        for key, command in enumerate(commands_list_):
            markup.add(
                types.InlineKeyboardButton(text=command[0], callback_data=command[1])
            )

    return {"str_to_send": str_to_send, "keyboard": markup}


@bot.message_handler(commands=["crimes"])
def crimes(message, lang):
    keyboard = types.ReplyKeyboardMarkup(
        one_time_keyboard=True, row_width=1, resize_keyboard=True
    )
    notification = "error 404"

    if lang == "ru":
        button_location = types.KeyboardButton(
            text=phrases_ru.SEND_GEO, request_location=True
        )
        notification = phrases_ru.ONCLICK_LOCATION_BUTTON
        keyboard.add(button_location)

    elif lang == "kz":
        button_location = types.KeyboardButton(
            text=phrases_kz.SEND_GEO, request_location=True
        )
        notification = phrases_kz.ONCLICK_LOCATION_BUTTON
        keyboard.add(button_location)

    message_counter(message.chat.id)
    bot.send_message(message.chat.id, notification, reply_markup=keyboard)
    set_user_action(tg_id=message.chat.id, action="static")


@bot.message_handler(content_types=["location"])
def location(message):
    action = get_user_action(message.chat.id)
    if message.location is not None:
        if action == "static":
            bot.lang = get_user_lang(message.chat.id)
            set_geo_user(
                tg_id=message.chat.id,
                geo=[message.location.latitude, message.location.longitude],
            )
            message_counter(message.chat.id)

            if bot.lang == "ru":
                bot.send_message(message.chat.id, phrases_ru.CONFIRM_REQUEST)
            elif bot.lang == "kz":
                bot.send_message(message.chat.id, phrases_kz.CONFIRM_REQUEST)

            get_crimes_in_radius(message)

        else:
            bot.lang = get_user_lang(message.chat.id)
            set_geo_user(
                tg_id=message.chat.id,
                geo=[message.location.latitude, message.location.longitude],
            )
            message_counter(message.chat.id)
            bot.send_message(message.chat.id, phrases_ru.CONFIRM_POINT)
            tm.sleep(1)  # wait
            lang = get_user_lang(message.chat.id)
            commands = commands_list(lang)
            bot.send_message(
                message.chat.id,
                commands["str_to_send"],
                reply_markup=commands["keyboard"],
            )


def get_crimes_in_radius(message):
    sqlalchemy_session = session()

    features: List[Features] = (
        sqlalchemy_session.query(Features)
        .order_by(Features.dat_sover.desc())
        .limit(10000)
        .all()
    )

    in_range = list()
    counter_crimes = 0

    for data in features:
        radius = get_user_set_radius(message.from_user.id)
        res = haversine(
            message.location.latitude,
            message.location.longitude,
            float(data.x_geo),
            float(data.y_geo),
            radius,
        )

        bot.send_chat_action(message.chat.id, action="typing")
        if res:
            if counter_crimes <= 2:
                in_range.append(data)
                counter_crimes += 1
            else:
                break

    count = len(in_range)
    lat_list = list()
    lon_list = list()

    if count > 0:
        counter = 0
        url_format = ""
        param_list = []

        for data in in_range:
            crime = get_crime_codes(data.crime_code)
            lat_list.append(float(data.x_geo))
            lon_list.append(float(data.y_geo))
            url_format += generate_maps_pins_url(counter, in_range, message, data)
            time = datetime.utcfromtimestamp(int(data.dat_sover) / 1000).strftime(
                "%d-%m-%Y / %H:%M"
            )
            param_list.append(
                [counter + 1, data.fz1r18p5, data.fz1r18p6, crime, time, data.stat]
            )
            counter += 1
        photo_list = generate_and_send_stat_map_jpg(url_format, message, bot)

        while True:
            try:
                lang = get_user_lang(message.chat.id)
                telegraph_link = create_telegraph(
                    param_list, photo_list["pic_list"], lang
                )
                bot.send_message(message.chat.id, telegraph_link)
                break

            except Exception as e_info:
                logger.error(e_info)
                continue

        tm.sleep(1)  # wait
        lang = get_user_lang(message.chat.id)
        commands = commands_list(lang)
        bot.send_message(
            message.chat.id, commands["str_to_send"], reply_markup=commands["keyboard"]
        )

    else:
        lang = get_user_lang(message.chat.id)
        if lang == "ru":
            commands = commands_list(lang)
            bot.send_message(
                message.chat.id,
                commands["str_to_send"],
                reply_markup=commands["keyboard"],
            )

            bot.send_message(message.chat.id, phrases_ru.NO_CRIMES)

        elif lang == "kz":
            commands = commands_list(lang)
            bot.send_message(
                message.chat.id,
                commands["str_to_send"],
                reply_markup=commands["keyboard"],
            )
            bot.send_message(message.chat.id, phrases_kz.NO_CRIMES)
        tm.sleep(1)
        lang = get_user_lang(message.chat.id)
        commands = commands_list(lang)
        bot.send_message(
            message.chat.id, commands["str_to_send"], reply_markup=commands["keyboard"]
        )


@bot.message_handler(commands=["last_20"])
def handle_last_20(message):
    sqlalchemy_session = session()

    features: List[Features] = (
        sqlalchemy_session.query(Features)
        .order_by(Features.dat_sover.desc())
        .limit(10000)
        .all()
    )

    bot.send_chat_action(message.chat.id, action="typing")
    param_list = []

    for data in features:
        try:
            time = datetime.utcfromtimestamp(data.dat_vozb).strftime("%d-%m-%Y / %H:%M")
            crime = get_crime_codes(data.crime_code)

            param_list.append([data.fz1r18p5, data.fz1r18p6, crime, time, data.stat])
        except Exception as e_info:
            logger.error(e_info)

    lang = get_user_lang(message.chat.id)
    telegraph_link = create_telegraph_for_all_crimes(param_list, lang)
    bot.send_message(message.chat.id, telegraph_link)

    tm.sleep(1)
    lang = get_user_lang(message.chat.id)
    commands = commands_list(lang)
    bot.send_message(
        message.chat.id, commands["str_to_send"], reply_markup=commands["keyboard"]
    )


if __name__ == '__main__':
    import logging.config
    import json


    def setup_logging(path: str = "./logging.json") -> None:
        with open(path, "rt") as f:
            config = json.load(f)
        logging.config.dictConfig(config)


    setup_logging()
    bot.polling(none_stop=True, interval=1)
