from django.contrib import admin

# Register your models here.
from .models import FlightEvent

@admin.register(FlightEvent)
class FlightEventAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'departure_city', 'arrival_city', 'departure_datetime')
    list_filter = ('departure_city', 'arrival_city')
    search_fields = ('flight_number', 'departure_city', 'arrival_city')