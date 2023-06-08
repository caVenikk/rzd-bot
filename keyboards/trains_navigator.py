import logging
from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from utils.models import Train

__all__ = ["TrainsNavigator"]


@dataclass(frozen=True)
class _Actions:
    prev = "prev"
    next = "next"


class _TrainsNavigator:
    def __init__(self, trains: list[Train], count: int, callback_data: CallbackData):
        self.__count: int = count
        self.__end: int = count
        self.__start: int = 0
        self.__trains: list[Train] = trains
        self._data = callback_data

    def build_text_and_markup(self, callback_data):
        markup = InlineKeyboardMarkup(row_width=2)
        text = ""
        if callback_data is not None:
            match callback_data["action"]:
                case _Actions.next:
                    self._next()
                case _Actions.prev:
                    self._prev()
        for index, train in enumerate(self.__trains[self.__start : self.__end]):
            car_with_min_price = min(train.cars, key=lambda car: car.tariff)
            path = f"<b>{train.station0}</b> ➡️ <b>{train.station1}</b>"
            if not train.is_departure_station_are_start:
                path = f"<i>{train.route0}</i> ➡️ " + path
            if not train.is_arrival_station_are_end:
                path += f" ➡️ <i>{train.route1}</i>"
            path += "\n"

            if self.__start == 0 and index == 0:
                text += "🔥<b><i>Самый дешевый:</i></b>\n"
            text += (
                f"<b>{train.number}</b> 🔘 {train.date0.strftime('%d.%m.%Y %H:%M')} ➖ "
                f"{train.date1.strftime('%d.%m.%Y %H:%M')}\n"
                f"(<i>Время в пути:</i> {train.time_in_way_string})\n"
                f"{path}"
                f"<b>Тип вагона</b>: {car_with_min_price.type}\n"
                f"<b>Цена</b>: от <i>{car_with_min_price.tariff}</i> ₽ "
                f"{'(Места для инвалидов)' if car_with_min_price.disabled_person else ''}"
                f"{'(Невозвратный тариф)' if car_with_min_price.non_refundable else ''}\n\n"
            )
        if len(self.__trains) > self.__count:
            if self.__start == 0:
                markup.add(
                    InlineKeyboardButton(text=" ", callback_data="_"),
                    InlineKeyboardButton(text="➡️", callback_data=self._data.new(_Actions.next, 0)),
                )
            elif self.__end >= len(self.__trains):
                markup.add(
                    InlineKeyboardButton(text="⬅️", callback_data=self._data.new(_Actions.prev, 0)),
                    InlineKeyboardButton(text=" ", callback_data="_"),
                )
            else:
                markup.add(
                    InlineKeyboardButton(text="⬅️", callback_data=self._data.new(_Actions.prev, 0)),
                    InlineKeyboardButton(text="➡️", callback_data=self._data.new(_Actions.next, 0)),
                )
        return text, markup

    def _next(self):
        if self.__start >= len(self.__trains) - self.__count:
            self.__end = self.__count
            self.__start = 0
        else:
            self.__start += self.__count
            self.__end += self.__count

    def _prev(self):
        if self.__start == 0:
            _start = (len(self.__trains) // self.__count) * self.__count
            self.__start = _start if _start != len(self.__trains) else _start - self.__count
            self.__end = self.__start + self.__count
        else:
            self.__start -= self.__count
            self.__end -= self.__count


class TrainsNavigator:
    _storage: dict[int, _TrainsNavigator] = dict()
    data = CallbackData("trains", "action", "train_number")
    actions = _Actions()

    @classmethod
    def setup(cls, trains: list[Train], user_id: int, count: int = 5):
        cls._storage[user_id] = _TrainsNavigator(trains=trains, count=count, callback_data=cls.data)

    @classmethod
    def clear(cls, user_id):
        try:
            del cls._storage[user_id]
        except KeyError as err:
            logging.exception(err)

    @classmethod
    def text_and_markup(cls, user_id, callback_data=None):
        try:
            return cls._storage[user_id].build_text_and_markup(callback_data)
        except KeyError:
            return None, None
