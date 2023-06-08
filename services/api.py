import asyncio
from datetime import datetime

import aiohttp

from utils.models import Station, Train, Car


async def get_stations(query: str) -> list[Station] | None:
    async with aiohttp.ClientSession() as session:
        api_url = (
            "https://ticket.rzd.ru/api/v1/suggests"
            "?GroupResults=true"
            "&RailwaySortPriority=true"
            "&MergeSuburban=true"
            f"&Query={query}"
            "&TransportType=rail"
        )
        async with session.get(api_url) as resp:
            stations_info = await resp.json(content_type=None)
    if not stations_info.get("train", None) and not stations_info.get("city", None):
        return None
    stations = [
        Station(
            country_code=station["countryIso"],
            express_code=station["expressCode"],
            name=station["name"],
            node_id=station["nodeId"],
        )
        for station in (stations_info["city"] + stations_info["train"])
    ]
    return stations


async def get_trains(code0: int, code1: int, date_: datetime) -> list[Train] | None:
    async with aiohttp.ClientSession() as session:
        api_rid_url = (
            "https://pass.rzd.ru/timetable/public/?layer_id=5827"
            "&dir=0"
            f"&code0={code0}"
            f"&code1={code1}"
            "&tfl=3"
            "&checkSeats=1"
            f"&dt0={date_.strftime('%d.%m.%Y')}"
            "&md=0"
        )
        async with session.get(api_rid_url) as resp:
            data = await resp.json(content_type=None)
        if data["result"] != "RID":
            return None
        rid = data["RID"]
        await asyncio.sleep(5)
        api_url = f"https://pass.rzd.ru/timetable/public/ru?layer_id=5827&rid={rid}"
        async with session.post(api_url) as resp:
            data_ = await resp.json(content_type=None)
    try:
        train_dicts = data_["tp"][0]["list"]
        trains = [
            Train(
                number=train["number"],
                code0=train["code0"],
                code1=train["code1"],
                station0=train["station0"],
                station1=train["station1"],
                route0=train["route0"],
                route1=train["route1"],
                date0=datetime.strptime(f"{train['date0']} {train['time0']}", "%d.%m.%Y %H:%M"),
                date1=datetime.strptime(f"{train['date1']} {train['time1']}", "%d.%m.%Y %H:%M"),
                cars=[
                    Car(
                        type=car["typeLoc"],
                        free_seats=car["freeSeats"],
                        tariff=car["tariff"],
                        disabled_person=car.get("disabledPerson", False),
                        non_refundable=car.get("nonRefundable", False),
                    )
                    for car in train["cars"]
                ],
            )
            for train in train_dicts
        ]
        return trains
    except KeyError:
        return None
