from mission_planner.models import Airport
import csv


def run():
    with open('scripts/data/icao_exports.csv') as file:
        reader = csv.reader(file)
        next(reader)

        Airport.objects.all().delete()

        for row in reader:
            airport = Airport(
                icao_sign=row[1],
                latitude=row[4],
                longitude=row[3],
            )

            airport.save()

            # print(row)