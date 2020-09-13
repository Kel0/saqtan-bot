import os
import random
import time as tm

import requests

from .utils import utm_to_lat_lng


def generate_maps_pins_url(counter, in_range, message, data):
    """Generate part of url for pins of crimes"""
    url_format = f"{message.location.longitude},{message.location.latitude},pm2bll~"
    geo_cords = utm_to_lat_lng(42, float(data.x_geo), float(data.y_geo))

    if counter + 1 == len(in_range[:10]):
        code = f"pm2rdl{counter + 1}"
        url_format += f"{geo_cords[1]},{geo_cords[0]},{code}"

    else:
        code = f"pm2rdl{counter + 1}"
        url_format += f"{geo_cords[1]},{geo_cords[0]},{code}~"

    return url_format


def generate_and_send_stat_map_jpg(url_format, message, bot):
    """Generate pic. with pins of crimes. Save it and send it"""
    photo_list = list()
    parent_dir = os.path.dirname(os.getcwd())

    while True:
        try:
            url = f"https://static-maps.yandex.ru/1.x/?l=map&pt={url_format}"
            print(url)
            resp = requests.get(url, stream=True)
            rand_session = random.randint(1, 10000000)
            filename = f"{parent_dir}/saqtan-bot/stat_map_jpg/static_map-{rand_session}_{int(tm.time())}.jpg"

            if resp.status_code == 200:
                with open(filename, "wb+") as file:
                    for chunk in resp.iter_content(1024):
                        file.write(chunk)

            with open(filename, "rb") as photo:
                bot.send_photo(message.chat.id, photo)
                photo_list.append(filename)
            break
        except FileNotFoundError as e_info:
            print(e_info)
            continue

    return {"pic_list": photo_list}
