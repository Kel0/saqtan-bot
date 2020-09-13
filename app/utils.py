import logging
import math
import time
from math import asin, cos, radians, sin, sqrt
from typing import List, Optional, Tuple

from .database.db import session
from .database.models import CrimeCodes, Users

logger = logging.getLogger(__name__)


def get_user_lang(tg_id: int) -> Optional[str]:
    """Get user's language by telegram id

    :param tg_id: Telegram id
    :return user.lang: User's chosen language
    :return None: if user not found"""
    sqlalchemy_session = session()

    user: Optional[Users] = (
        sqlalchemy_session.query(Users)
        .filter(Users.telegram_id == tg_id)
        .limit(1)
        .one()
    )

    if user is not None:
        return user.lang

    return None


def message_counter(tg_id: int) -> None:
    """Update user's message count

    :param tg_id: Telegram id
    :return None:"""
    sqlalchemy_session = session()

    (
        sqlalchemy_session.query(Users)
        .filter(Users.telegram_id == tg_id)
        .update({Users.messages_count: Users.messages_count + 1})
    )
    sqlalchemy_session.commit()


def get_user_set_radius(tg_id: int) -> Optional[int]:
    """Get radius of player

    :param tg_id: Telegram id
    :return radius: Radius which set by user"""
    sqlalchemy_session = session()

    try:
        radius: Optional[Tuple[int]] = (
            sqlalchemy_session.query(Users.radius)
            .filter(Users.telegram_id == tg_id)
            .limit(1)
            .one()
        )
        return radius[0]
    except Exception as e_info:
        logger.error(e_info)


def get_crime_codes(crime_code: str) -> Optional[CrimeCodes]:
    """Encode crime code

    :param crime_code: Crime code
    :return crime_desc[0]: CrimeCodes model object
    :return None: If len of crime_desc list is 0"""
    sqlalchemy_session = session()

    crime_code_encoded: str
    if crime_code[0] == "0":
        crime_code_encoded = f"{crime_code[1]}{crime_code[2]}"
    else:
        crime_code_encoded = crime_code[:-1]

    crime_desc: List[CrimeCodes] = (
        sqlalchemy_session.query(CrimeCodes)
        .filter(CrimeCodes.crime_code == crime_code_encoded)
        .limit(1)
        .all()
    )

    if len(crime_desc) == 0:
        return None

    return crime_desc[0]


def get_user_action(tg_id: int) -> Optional[Users]:
    """Get user's actions

    :param tg_id: Telegram id
    :return user[0]: Users's.action model attr
    :return None: If user not found"""
    sqlalchemy_session = session()

    user: List[Users] = (
        sqlalchemy_session.query(Users)
        .filter(Users.telegram_id == tg_id)
        .limit(1)
        .all()
    )
    if len(user) == 0:
        return None

    return user[0].action


def user_create(first_name: str, last_name: str, tg_id: int) -> bool:
    """Create user

    :param first_name: First name
    :param last_name: Last name
    :param tg_id: Telegram id"""
    sqlalchemy_session = session()

    # Check if user exist
    user: List[Users] = (
        sqlalchemy_session.query(Users)
        .filter(Users.telegram_id == tg_id)
        .limit(1)
        .all()
    )

    if len(user) > 0:
        return False

    elif len(user) == 0:
        tries: int = 0
        while True:
            try:
                sqlalchemy_session.add(
                    Users(
                        first_name=first_name,
                        last_name=last_name,
                        telegram_id=tg_id,
                        registration_date=int(time.time()),
                    )
                )
                sqlalchemy_session.commit()
                return True
            except Exception as e_info:
                if tries >= 3:
                    return False

                logger.error(f"{e_info} | TG_ID: {tg_id}")
                tries += 1
                continue


def set_radius(tg_id: int, radius: float = 1) -> None:
    """Set user's radius

    :param tg_id: Telegram id
    :param radius: Radius, by default = 1"""
    sqlalchemy_session = session()

    try:
        (
            sqlalchemy_session.query(Users)
            .filter(Users.telegram_id == tg_id)
            .update({Users.radius: radius})
        )
        sqlalchemy_session.commit()
    except Exception as e_info:
        logger.error(e_info)


def set_lang_user(tg_id: int, lang: Optional[str] = None) -> None:
    """Set user's lang

    :param tg_id: Telegram id
    :param lang: Chosen language"""
    sqlalchemy_session = session()

    try:
        (
            sqlalchemy_session.query(Users)
            .filter(Users.telegram_id == tg_id)
            .update({Users.lang: lang})
        )
        sqlalchemy_session.commit()
    except Exception as e_info:
        logger.error(e_info)


def set_geo_user(tg_id: int, geo: List[float]) -> None:
    """Set user's geolocation

    :param tg_id: Telegram id
    :param geo: List of [lat, lon]"""
    sqlalchemy_session = session()

    try:
        (
            sqlalchemy_session.query(Users)
            .filter(Users.telegram_id == tg_id)
            .update({Users.lat: geo[0], Users.lon: geo[1]})
        )
        sqlalchemy_session.commit()
    except Exception as e_info:
        logger.error(e_info)


def set_user_action(tg_id: int, action: str) -> None:
    """Set action for user

    :param tg_id: Telegram id
    :param action: User's action"""
    sqlalchemy_session = session()

    try:
        (
            sqlalchemy_session.query(Users)
            .filter(Users.telegram_id == tg_id)
            .update({Users.action: action})
        )
        sqlalchemy_session.commit()
    except Exception as e_info:
        logger.error(e_info)


def set_attach(tg_id: int, attach: int = 0):
    """Set user's attach status

    :param tg_id: Telegram id
    :param attach: Status of attach column, by default = 0"""
    sqlalchemy_session = session()

    try:
        (
            sqlalchemy_session.query(Users)
            .filter(Users.telegram_id == tg_id)
            .update({Users.attach: attach})
        )
        sqlalchemy_session.commit()
    except Exception as e_info:
        logger.error(e_info)


def haversine(lon1, lat1, lon2, lat2, radius):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles

    a = c * r
    if a <= radius:
        res = True
    else:
        res = False

    return res


def utm_to_lat_lng(zone, easting, northing, northern_hemisphere=True):
    if not northern_hemisphere:
        northing = 10000000 - northing

    a = 6378137
    e = 0.081819191
    e1sq = 0.006739497
    k0 = 0.9996

    arc = northing / k0
    mu = arc / (
        a
        * (
            1
            - math.pow(e, 2) / 4.0
            - 3 * math.pow(e, 4) / 64.0
            - 5 * math.pow(e, 6) / 256.0
        )
    )

    ei = (1 - math.pow((1 - e * e), (1 / 2.0))) / (1 + math.pow((1 - e * e), (1 / 2.0)))

    ca = 3 * ei / 2 - 27 * math.pow(ei, 3) / 32.0

    cb = 21 * math.pow(ei, 2) / 16 - 55 * math.pow(ei, 4) / 32
    cc = 151 * math.pow(ei, 3) / 96
    cd = 1097 * math.pow(ei, 4) / 512
    phi1 = (
        mu
        + ca * math.sin(2 * mu)
        + cb * math.sin(4 * mu)
        + cc * math.sin(6 * mu)
        + cd * math.sin(8 * mu)
    )

    n0 = a / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (1 / 2.0))

    r0 = a * (1 - e * e) / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (3 / 2.0))
    fact1 = n0 * math.tan(phi1) / r0

    _a1 = 500000 - easting
    dd0 = _a1 / (n0 * k0)
    fact2 = dd0 * dd0 / 2

    t0 = math.pow(math.tan(phi1), 2)
    Q0 = e1sq * math.pow(math.cos(phi1), 2)
    fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * math.pow(dd0, 4) / 24

    fact4 = (
        (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0)
        * math.pow(dd0, 6)
        / 720
    )

    lof1 = _a1 / (n0 * k0)
    lof2 = (1 + 2 * t0 + Q0) * math.pow(dd0, 3) / 6.0
    lof3 = (
        (5 - 2 * Q0 + 28 * t0 - 3 * math.pow(Q0, 2) + 8 * e1sq + 24 * math.pow(t0, 2))
        * math.pow(dd0, 5)
        / 120
    )
    _a2 = (lof1 - lof2 + lof3) / math.cos(phi1)
    _a3 = _a2 * 180 / math.pi

    latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / math.pi

    if not northern_hemisphere:
        latitude = -latitude

    longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3

    return latitude, longitude
