from django.db import models

# Create your models here.

class FlightEvent(models.Model):
    flight_number = models.CharField(max_length=10)
    departure_city = models.CharField(max_length=3)
    arrival_city = models.CharField(max_length=3)
    departure_datetime = models.DateTimeField()
    arrival_datetime = models.DateTimeField()

    class Meta:
        db_table = 'flight_event'

    def __str__(self):
        return f"{self.flight_number} - {self.departure_city} to {self.arrival_city}"