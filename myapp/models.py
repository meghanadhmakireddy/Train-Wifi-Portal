from django.db import models

class TrainPassenger(models.Model):
    pnr = models.CharField(max_length=10, unique=True)
    mobile_number = models.CharField(max_length=10)
    passenger_count = models.IntegerField()
    journey_active = models.BooleanField(default=True)

    def __str__(self):
        return self.pnr
