import logging
from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from utils.models import Station

__all__ = ["StationSelector"]


@dataclass(frozen=True)
class _Actions:
    prev = "prev"
    next = "next"
    back = "back"
    select = "select"


class _StationSelector:
    def __init__(self, stations: list[Station], count: int, callback_data: CallbackData):
        self.__count: int = count
        self.__end: int = count
        self.__start: int = 0
        self.__stations: list[Station] = stations
        self._data = callback_data

    def build_markup(self, callback_data):
        markup = InlineKeyboardMarkup(row_width=2)
        if callback_data is not None:
            match callback_data["action"]:
                case _Actions.next:
                    self._next()
                case _Actions.prev:
                    self._prev()
        for station in self.__stations[self.__start : self.__end]:
            _text = station.name
            markup.add(
                InlineKeyboardButton(text=_text, callback_data=self._data.new(_Actions.select, station.express_code))
            )
        if len(self.__stations) > self.__count:
            markup.add(
                InlineKeyboardButton(text="⬅️", callback_data=self._data.new(_Actions.prev, 0)),
                InlineKeyboardButton(text="➡️", callback_data=self._data.new(_Actions.next, 0)),
            )
        markup.add(InlineKeyboardButton(text="Назад ↩️", callback_data=self._data.new(_Actions.back, 0)))
        return markup

    def _next(self):
        if self.__start >= len(self.__stations) - self.__count:
            self.__end = self.__count
            self.__start = 0
        else:
            self.__start += self.__count
            self.__end += self.__count

    def _prev(self):
        if self.__start == 0:
            _start = (len(self.__stations) // self.__count) * self.__count
            self.__start = _start if _start != len(self.__stations) else _start - self.__count
            self.__end = self.__start + self.__count
        else:
            self.__start -= self.__count
            self.__end -= self.__count


class StationSelector:
    _storage: dict[int, _StationSelector] = dict()
    data = CallbackData("stations", "action", "station_code")
    actions = _Actions()

    @classmethod
    def setup(cls, stations: list[Station], user_id: int, count: int = 5):
        cls._storage[user_id] = _StationSelector(stations=stations, count=count, callback_data=cls.data)

    @classmethod
    def clear(cls, user_id):
        try:
            del cls._storage[user_id]
        except KeyError as err:
            logging.exception(err)

    @classmethod
    def markup(cls, user_id, callback_data=None):
        try:
            return cls._storage[user_id].build_markup(callback_data)
        except KeyError:
            pass
