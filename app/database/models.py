from sqlalchemy import Column, Float, ForeignKey, Integer, String

from .db import base


class Users(base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(length=255))
    last_name = Column(String(length=255))
    telegram_id = Column(Integer)
    messages_count = Column(Integer)
    registration_date = Column(Integer)
    lang = Column(String(length=10))
    radius = Column(Float)
    radius_stat = Column(Integer)
    lat = Column(String(length=100))
    lon = Column(String(length=100))
    action = Column(String(length=100))
    attach = Column(Integer)


class CrimeCodes(base):
    __tablename__ = "crime_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    crime_code = Column(Integer)
    crime_desc = Column(String(length=500), default="No desc")

    def __repr__(self):
        return f"<{self.__tablename__}(crime_code={self.crime_code}, crime_desc={self.crime_desc})>"


class Features(base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    object_id = Column(Integer, index=True, unique=True)
    year = Column(Integer, index=True)
    period = Column(Integer, index=True)
    crime_code = Column(String(length=10), index=True)
    time_period = Column(String(length=20), index=True)
    hard_code = Column(String(length=4), index=True)
    ud = Column(String(length=100), index=True)
    organ = Column(String(length=255), index=True)
    dat_vozb = Column(String(length=225), index=True)
    dat_sover = Column(String(length=225), index=True)
    stat = Column(String(length=255), index=True)
    dat_vozb_str = Column(String(length=255), index=True)
    dat_sover_str = Column(String(length=255), index=True)
    tz1id = Column(String(length=255), index=True)
    reg_code = Column(String(length=100), index=True)
    city_code = Column(Integer, ForeignKey("city_codes.city_code"), index=True)
    status = Column(Integer, index=True)
    org_code = Column(String(length=100), index=True)
    entrydate = Column(String(length=225), index=True)
    fz1r18p5 = Column(String(length=255), index=True)
    fz1r18p6 = Column(String(length=255), index=True)
    transgression = Column(String(length=255), index=True)
    organ_kz = Column(String(length=255), index=True)
    organ_en = Column(String(length=255), index=True)
    fe1r29p1_id = Column(String(length=100), index=True)
    fe1r32p1 = Column(String(length=255), nullable=True, index=True)
    x_geo = Column(String(length=255), index=True)
    y_geo = Column(String(length=255), index=True)

    def __repr__(self):
        return (
            f"<{self.__tablename__}(object_id={self.object_id}, year={self.year}, period={self.period}, "
            f"crime_code={self.crime_code}, time_period={self.time_period}, hard_code={self.hard_code}, "
            f"ud={self.ud}, organ={self.organ}, dat_vozb={self.dat_vozb}, dat_sover={self.dat_sover}, "
            f"stat={self.stat}, dat_vozb_str={self.dat_vozb_str}, dat_sover_str={self.dat_sover_str}, "
            f"tz1id={self.tz1id}, reg_code={self.reg_code}, city_code={self.city_code}, status={self.status}, "
            f"org_code={self.org_code}, entrydate={self.entrydate}, fz1r18p5={self.fz1r18p5}, "
            f"fz1r18p6={self.fz1r18p6}, transgression={self.transgression}, organ_kz={self.organ_kz}, "
            f"organ_en={self.organ_en}, fe1r29p1_id={self.fe1r29p1_id}, fe1r32p1={self.fe1r32p1}, "
            f"x_geo={self.x_geo}, y_geo={self.y_geo})>"
        )
