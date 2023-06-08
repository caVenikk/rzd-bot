from dataclasses import dataclass
from datetime import date


@dataclass
class Station:
    country_code: str
    express_code: int
    name: str
    node_id: str

    def __str__(self):
        return f"{self.express_code}: {self.name}"

    def __repr__(self):
        return f"{self.express_code}: {self.name}"

    def to_dict(self):
        return dict(
            country_code=self.country_code,
            express_code=self.express_code,
            name=self.name,
            node_id=self.node_id,
        )


@dataclass
class Car:
    type: str
    free_seats: int
    tariff: int
    disabled_person: bool = False
    non_refundable: bool = False

    def __str__(self):
        return f"{self.type}\t{self.free_seats}\tот {self.tariff}₽"

    def __repr__(self):
        return f"{self.type}\t{self.free_seats}\tот {self.tariff}₽"

    def to_dict(self):
        return dict(
            type=self.type,
            free_seats=self.free_seats,
            tariff=self.tariff,
            disabled_person=self.disabled_person,
            non_refundable=self.non_refundable,
        )


@dataclass
class Train:
    number: str
    code0: int
    code1: int
    station0: str
    station1: str
    route0: str
    route1: str
    date0: date
    date1: date
    cars: list[Car]

    @staticmethod
    def suffix(days: int):
        ending = days % 10
        if ending == 1:
            return "день"
        if ending > 4 or 4 < days < 21 or ending == 0:
            return "дней"
        return "дня"

    @property
    def time_in_way_string(self) -> str:
        time_in_way = self.date1 - self.date0
        days = time_in_way.days
        suffix = self.suffix(days)
        time_in_way_str = str(time_in_way)
        time_in_way_str = time_in_way_str.replace("days", suffix).replace("day", suffix)
        return time_in_way_str

    @property
    def is_departure_station_are_start(self):
        route_letters = set(self.route0.upper().replace("-", "").replace(" ", ""))
        station_letters = set(self.station0.upper().replace(" ", "").replace("-", ""))

        return route_letters.issubset(station_letters) and self.route0[0] == self.station0[0]

    @property
    def is_arrival_station_are_end(self):
        route_letters = set(self.route1.upper().replace("-", "").replace(" ", ""))
        station_letters = set(self.station1.upper().replace(" ", "").replace("-", ""))

        return route_letters.issubset(station_letters) and self.route1[0] == self.station1[0]

    def __str__(self):
        return f"{self.number}·{self.date0.strftime('%d.%m.%Y %H:%M')}\n{self.station0}→{self.station1}→{self.route1}"

    def __repr__(self):
        return f"{self.number}·{self.date0.strftime('%d.%m.%Y %H:%M')}\n{self.station0}→{self.station1}→{self.route1}"

    def to_dict(self):
        return dict(
            number=self.number,
            code0=self.code0,
            code1=self.code1,
            station0=self.station0,
            station1=self.station1,
            route0=self.route0,
            route1=self.route1,
            date0=self.date0,
            date1=self.date1,
            time_in_way=self.time_in_way_string,
            cars=self.cars,
        )
