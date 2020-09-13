from typing import Any, List, Union

from telegraph import Telegraph

PARAM_LIST = List[List[Union[Union[int, None, str], Any]]]


def create_telegraph(param_list: PARAM_LIST, photo_list, lang) -> str:
    telegraph = Telegraph()
    telegraph.create_account(short_name="SaqtanBot2")
    html_content: str = ""

    if lang == "ru":
        for photo in photo_list:
            html_content += f'<img src="{photo}" alt="map" />'

        for data in param_list:
            html_content += f"<p>id: {data[0]}</p>"
            html_content += f"<p>🛣Где произошло: {data[1]} - {data[2]}</p>"
            html_content += f"<p>🕵🏻‍♂Тип преступления: {data[3]}</p>"
            html_content += f"<p>⏰Время совершенного преступления: {data[4]}</p>"
            html_content += f"<p>🔖Статья: {data[5]}</p>"
            html_content += f"<p>__________________________</p>"

        response = telegraph.create_page("Преступения!", html_content=html_content)

        return f"https://telegra.ph/{response['path']}"

    elif lang == "kz":
        for photo in photo_list:
            html_content += f'<img src="{photo}" alt="map" />'

        for data in param_list:
            html_content += f"<p>id: {data[0]}</p>"
            html_content += f"<p>🛣Где произошло: {data[1]} - {data[2]}</p>"
            html_content += f"<p>🕵🏻‍♂Тип преступления: {data[3]}</p>"
            html_content += f"<p>⏰Время совершенного преступления: {data[4]}</p>"
            html_content += f"<p>🔖Статья: {data[5]}</p>"
            html_content += f"<p>__________________________</p>"

        response = telegraph.create_page("Қылмыстар!", html_content=html_content)

        return f"https://telegra.ph/{response['path']}"


def create_telegraph_for_all_crimes(param_list, lang) -> str:
    telegraph = Telegraph()
    telegraph.create_account(short_name="SaqtanBot2")
    html_content = ""

    if lang == "ru":
        for data in param_list:
            html_content += f"<p>🛣Где произошло: {data[0]} - {data[1]}</p>"
            html_content += f"<p>🕵🏻‍♂Тип преступления: {data[2]}</p>"
            html_content += f"<p>⏰Время совершенного преступления: {data[3]}</p>"
            html_content += f"<p>🔖Статья: {data[4]}</p>"
            html_content += f"<p>__________________________</p>"
        print(html_content)
        response = telegraph.create_page("Преступения!", html_content=html_content)

        return f"https://telegra.ph/{response['path']}"

    elif lang == "kz":
        for data in param_list:
            html_content += f"<p>🛣Где произошло: {data[0]} - {data[1]}</p>"
            html_content += f"<p>🕵🏻‍♂Тип преступления: {data[2]}</p>"
            html_content += f"<p>⏰Время совершенного преступления: {data[3]}</p>"
            html_content += f"<p>🔖Статья: {data[4]}</p>"
            html_content += f"<p>__________________________</p>"

        response = telegraph.create_page("Преступения!", html_content=html_content)

        return f"https://telegra.ph/{response['path']}"
