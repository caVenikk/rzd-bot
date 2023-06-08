import calendar
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

__all__ = ["DateSelector"]


@dataclass(frozen=True)
class _Actions:
    prev_month = "prev_month"
    next_month = "next_month"
    select_day = "select_day"
    confirm = "confirm"


class _DateSelector:
    def __init__(self, callback_data):
        self.current_date = datetime.now()
        self.data = callback_data
        self.year = self.current_date.year
        self.month = self.current_date.month
        self.selected_day = 0
        self.selected_month = 0
        self.selected_year = 0

    def build_markup(self, callback_data):
        self._callback_data_handler(callback_data)
        markup = InlineKeyboardMarkup(row_width=7)
        self._build_year(markup)
        self._build_month(markup)
        self._build_weekdays(markup)
        self._build_days(markup)
        self._build_confirm(markup)
        return markup

    def _callback_data_handler(self, callback_data):
        if callback_data is None:
            return
        match callback_data["action"]:
            case _Actions.select_day:
                day = int(callback_data["day"])
                year = int(callback_data["year"])
                month = int(callback_data["month"])
                if day == self.selected_day and year == self.selected_year and self.selected_month == month:
                    self.selected_day = 0
                else:
                    self.selected_day, self.selected_year, self.selected_month = day, year, month
            case _Actions.next_month:
                _date = datetime(self.year, self.month, 1) + timedelta(days=31)
                self.month, self.year = _date.month, _date.year
            case _Actions.prev_month:
                _date = datetime(self.year, self.month, 1) - timedelta(days=1)
                self.month, self.year = _date.month, _date.year

    def _build_year(self, markup):
        markup.add(InlineKeyboardButton(str(self.year), callback_data="_"))
        return markup

    def _build_month(self, markup):
        markup.add(
            InlineKeyboardButton(
                "◀️" if self.month != self.current_date.month else " ",
                callback_data=self.data.new(_Actions.prev_month, self.year, self.month, 0)
                if self.month != self.current_date.month
                else "_",
            ),
            InlineKeyboardButton(str(calendar.month_name[self.month]), callback_data="_"),
            InlineKeyboardButton("▶️", callback_data=self.data.new(_Actions.next_month, self.year, self.month, 0)),
        )
        return markup

    @staticmethod
    def _build_weekdays(markup):
        markup.add(*(InlineKeyboardButton(str(weekday), callback_data="_") for weekday in calendar.day_abbr))
        return markup

    def _build_days(self, markup):
        month = calendar.monthcalendar(self.year, self.month)
        for week in month:
            markup.row()
            for day in week:
                if day == 0 or self.month == self.current_date.month and day < self.current_date.day:
                    markup.insert(InlineKeyboardButton(" ", callback_data="_"))
                else:
                    markup.insert(
                        InlineKeyboardButton(
                            self._mark_day(day),
                            callback_data=self.data.new(_Actions.select_day, self.year, self.month, day),
                        )
                    )
        return markup

    def _build_confirm(self, markup):
        if self.selected_day != 0:
            markup.add(
                InlineKeyboardButton(
                    f"❕Подтвердить {self.selected_day:02d}.{self.selected_month:02d}.{self.selected_year}❔",
                    callback_data=self.data.new(
                        _Actions.confirm, self.selected_year, self.selected_month, self.selected_day
                    ),
                )
            )
        else:
            markup.add(InlineKeyboardButton(" ", callback_data="_"))
        return markup

    def _mark_day(self, day):
        if self.year == self.selected_year and self.month == self.selected_month:
            return day if day != self.selected_day else "✅"
        else:
            return day


class DateSelector:
    _storage: dict[int, _DateSelector] = dict()
    data = CallbackData("calendar", "action", "year", "month", "day")
    actions = _Actions()

    @classmethod
    def setup(cls, user_id):
        cls._storage[user_id] = _DateSelector(callback_data=cls.data)

    @classmethod
    def markup(cls, user_id, callback_data=None):
        try:
            return cls._storage[user_id].build_markup(callback_data=callback_data)
        except KeyError:
            pass

    @classmethod
    def clear(cls, user_id):
        try:
            del cls._storage[user_id]
        except KeyError as err:
            logging.exception(str(err))

    @classmethod
    def users(cls):
        return cls._storage.keys()
