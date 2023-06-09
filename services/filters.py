from utils.models import Train


def sorted_trains_by_price(trains: list[Train]) -> list[Train]:
    return sorted(trains, key=lambda train: min(car.tariff for car in train.cars))


def filtered_without_disabled(trains: list[Train]) -> list[Train]:
    for train in trains.copy():
        train.cars = [car for car in train.cars if not car.disabled_person]
    return trains
