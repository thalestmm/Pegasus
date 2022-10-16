from django.db import models

# Create your models here.


class Airport(models.Model):
    # BASIC DATA
    icao_sign     = models.CharField(max_length=4, primary_key=True)
    latitude      = models.FloatField()
    longitude     = models.FloatField()

    # FUELING DATA
    has_fueling   = models.BooleanField(default=False)
    # TODO: ADD LOGIC TO CHANGE VALUES FROM READING THE CELOG TABLE

    def __str__(self):
        return self.icao_sign


class Project(models.Model):
    # AIRCRAFT REGISTRY DATA
    registry           = models.CharField(primary_key=True, max_length=10)
    aircraft_type      = models.CharField(max_length=10)

    # PERFORMANCE DATA
    cruising_speed     = models.IntegerField()
    operational_weight = models.IntegerField()
    max_takeoff_weight = models.IntegerField()
    max_fuel           = models.IntegerField()
    fuel_burn          = models.IntegerField()

    FUEL_CHOICES       = [
        ('LB', 'pounds'),
        ('KG', 'kilograms')
    ]
    fuel_unit          = models.CharField(max_length=2, choices=FUEL_CHOICES)
    # TODO: MAKE THE PROPER ADJUSTMENTS TO THE WEIGHTS

    def __str__(self):
        return str(self.aircraft_type + ' ' + self.registry)
