import datetime

from mission_planner.models import Project, Airport
from typing import Dict, Tuple, List
from datetime import time, timedelta
from haversine import haversine, Unit
from math import ceil


class FlightPlan:
    def __init__(self, project: Project, trip_weight: int,
                 takeoff_time: time, flight_plan_legs: Dict,
                 procedure_time: int = 20):
        self.project = project  # PROJECT INSTANCE FROM FORM
        self.trip_weight = trip_weight
        self.takeoff_time = takeoff_time
        self.flight_plan_legs = flight_plan_legs

        self.procedure_time_minutes = procedure_time

        self.total_hours   = timedelta(hours=0)
        self.working_hours = timedelta(hours=0)

        self.all_fpl_airports = []

        self.adjusted_legs = self.adjust_legs_format()
        self.export_data = []

        self.icao_route = []

        for index, leg in enumerate(self.adjusted_legs):
            output = self.leg_full_execution(
                org_ICAO=leg['org'],
                des_ICAO=leg['des'],
                alt_ICAO=leg['altn']
            )

            if index == 0:
                self.icao_route.append(leg['org'])
            else:
                self.icao_route.append(leg['des'])

            self.export_data.append(output)

        self.total_hours   = self.prettify_time(self.total_hours)
        self.working_hours = self.prettify_time(self.working_hours)

    def adjust_legs_format(self) -> List[Dict]:
        """
        Transform the raw package data into a list of Dicts
        :return: List[Dict]
        """
        adjusted_legs = []
        counter = 0

        while True:
            if self.flight_plan_legs.__contains__(f'dep_{counter}'):
                pass
            else:
                break

            org = self.flight_plan_legs[f'dep_{counter}']
            des = self.flight_plan_legs[f'arr_{counter}']
            altn = self.flight_plan_legs[f'alt_{counter}']

            leg_dict = {
                "org": org,
                "des": des,
                "altn": altn
            }

            adjusted_legs.append(leg_dict)

            counter += 1

        return adjusted_legs

    @staticmethod
    def get_coordinates(icao_sign: str) -> Tuple[float, float]:
        if icao_sign == '':
            return None

        try:
            latitude = Airport.objects.get(icao_sign=icao_sign).latitude
            longitude = Airport.objects.get(icao_sign=icao_sign).longitude
            return latitude, longitude

        except:
            raise IndexError("ICAO sign not available")

    def get_distance(self, ICAO_1: str, ICAO_2: str) -> float:
        coords_1 = self.get_coordinates(ICAO_1)
        coords_2 = self.get_coordinates(ICAO_2)

        return float(haversine(coords_1, coords_2, unit=Unit.NAUTICAL_MILES))

    def find_nearest_alternative(self, arr_ICAO: str):
        # TODO: ADD NEAREST ALTN LOGIC
        available_fueling_airports = Airport.objects.all().filter(has_fueling=True)

        nearest_airport = ("SBCO", float('inf'))

        for airport in available_fueling_airports:
            if airport.__str__() == arr_ICAO:
                nearest_airport = nearest_airport
            else:
                distance = self.get_distance(arr_ICAO, airport)

                if distance < nearest_airport[1]:
                    nearest_airport = (airport, distance)

        return nearest_airport[0].__str__()

    def list_all_airports_from_fpl(self):
        pass

    def get_time_from_distance_minutes(self, distance: float,
                                       procedure_time: bool = True) -> int:
        time = ceil((distance / self.project.cruising_speed) * 60)

        if time % 10 == 0:
            rounded_time_in_minutes = time
        else:
            time = time // 5
            rounded_time_in_minutes = (time * 5) + 5

        if procedure_time:
            return rounded_time_in_minutes + self.procedure_time_minutes

        else:
            return rounded_time_in_minutes

    def minimum_leg_fuel(self, main_time: int, altn_time: int) -> int:
        burn_per_minute = self.project.fuel_burn / 60

        main_burn = main_time * burn_per_minute
        altn_burn = altn_time * burn_per_minute

        total_burn = main_burn + altn_burn + (45 * burn_per_minute)

        return ceil(total_burn)

    def get_available_leg_weight(self, leg_fuel):
        if self.project.fuel_unit == 'LB':
            fuel_weight = leg_fuel * 0.45
        else:
            fuel_weight = leg_fuel

        disponibilidade = self.project.max_takeoff_weight
        disponibilidade -= self.project.operational_weight
        disponibilidade -= self.trip_weight
        disponibilidade -= fuel_weight

        return int(disponibilidade)

    @staticmethod
    def hours_from_minutes(time_in_minutes) -> Tuple[int, int]:
        hours = int(time_in_minutes // 60)
        minutes = int(time_in_minutes - (60 * hours))

        return hours, minutes

    def prettify_time(self, time_obj: timedelta) -> str:
        raw_minutes = time_obj.seconds / 60
        hours, minutes = self.hours_from_minutes(raw_minutes)

        return f'{str(hours).zfill(2)}:{str(minutes).zfill(2)}'

    def leg_full_execution(self, org_ICAO: str, des_ICAO: str, alt_ICAO: str):
        if org_ICAO == '' or des_ICAO == '':
            return None

        if alt_ICAO == '':
            alt_ICAO = self.find_nearest_alternative(des_ICAO)

        main_distance = self.get_distance(org_ICAO, des_ICAO)

        if alt_ICAO == '':
            alternative = self.find_nearest_alternative(des_ICAO)
        else:
            alternative = alt_ICAO

        self.all_fpl_airports.append(org_ICAO) if org_ICAO not in self.all_fpl_airports else self.all_fpl_airports
        self.all_fpl_airports.append(des_ICAO) if des_ICAO not in self.all_fpl_airports else self.all_fpl_airports
        self.all_fpl_airports.append(alternative) if alternative not in self.all_fpl_airports else self.all_fpl_airports

        alt_distance = self.get_distance(des_ICAO, alternative)

        main_time = self.get_time_from_distance_minutes(main_distance)
        altn_time = self.get_time_from_distance_minutes(alt_distance, procedure_time=False)

        min_leg_fuel = self.minimum_leg_fuel(main_time=main_time, altn_time=altn_time)

        disponibilidade = self.get_available_leg_weight(leg_fuel=min_leg_fuel)

        takeoff_hour, takeoff_minutes = self.takeoff_time.hour, self.takeoff_time.minute
        takeoff_timedelta = timedelta(hours=takeoff_hour, minutes=takeoff_minutes)

        main_hours, main_minutes = self.hours_from_minutes(main_time)

        altn_hours, altn_minutes = self.hours_from_minutes(altn_time)



        # EXPORT API
        eobt = takeoff_timedelta
        eobt = self.prettify_time(eobt)

        org = org_ICAO

        eta = takeoff_timedelta + timedelta(hours=main_hours, minutes=main_minutes)
        # TAKEOFF TIME UPDATE
        self.takeoff_time = (datetime.datetime.min + eta + timedelta(hours=1)).time()
        eta = self.prettify_time(eta)

        des = des_ICAO

        tev = timedelta(hours=main_hours, minutes=main_minutes)
        # UPDATE TOTAL HOURS
        self.total_hours += tev
        self.working_hours += tev + timedelta(hours=1)

        tev = self.prettify_time(tev)

        altn = alternative

        talt = timedelta(hours=altn_hours, minutes=altn_minutes)
        talt = self.prettify_time(talt)

        disp = disponibilidade

        try:
            org_has_fueling  = Airport.objects.all().get(icao_sign=org).has_fueling
            des_has_fueling  = Airport.objects.all().get(icao_sign=des).has_fueling
            altn_has_fueling = Airport.objects.all().get(icao_sign=altn).has_fueling
        except:
            org_has_fueling  = False
            des_has_fueling  = False
            altn_has_fueling = False

        export_dict = {
            'eobt': eobt,
            'org': org,
            'eta': eta,
            'des': des,
            'tev': tev,
            'min_leg_fuel': min_leg_fuel,
            'altn': altn,
            'talt': talt,
            'disp': disp,
            'org_has_fueling': org_has_fueling,
            'des_has_fueling': des_has_fueling,
            'altn_has_fueling': altn_has_fueling
        }
        self.find_nearest_alternative("SNXX")
        return export_dict

    def __str__(self):
        return str(self.project)
