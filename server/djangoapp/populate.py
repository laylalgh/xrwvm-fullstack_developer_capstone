import json
from pathlib import Path

from django.db import transaction

from .models import CarMake, CarModel


@transaction.atomic
def initiate():
    data_path = Path(__file__).resolve().parents[1] / "database/data/car_records.json"
    cars = json.loads(data_path.read_text())["cars"]
    known_types = dict(CarModel._meta.get_field("type").choices)
    for car in cars:
        make, _ = CarMake.objects.get_or_create(name=car["make"])
        kind = car["bodyType"].title()
        CarModel.objects.update_or_create(
            car_make=make, name=car["model"], year=car["year"],
            defaults={"type": kind if kind in known_types else "Other"},
        )
