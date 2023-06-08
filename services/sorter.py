from utils.models import Train


def sorted_trains_by_price(trains: list[Train]) -> list[Train]:
    return sorted(trains, key=lambda train: min(car.tariff for car in train.cars))
