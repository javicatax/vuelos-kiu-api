import requests
from django.core.management.base import BaseCommand
from flights.models import FlightEvent
from datetime import datetime

MOCK_API_URL = "https://mock.apidog.com/m1/814105-793312-default/flight-events"

class Command(BaseCommand):
    help = 'Loads flight events from an external API'

    def handle(self, *args, **options):
        url = MOCK_API_URL
        response = requests.get(url)
        data = response.json()

        for item in data:
            FlightEvent.objects.update_or_create(
                flight_number=item['flight_number'],
                departure_city=item['departure_city'],
                arrival_city=item['arrival_city'],
                departure_datetime=datetime.fromisoformat(item['departure_datetime'].replace('Z', '+00:00')),
                arrival_datetime=datetime.fromisoformat(item['arrival_datetime'].replace('Z', '+00:00'))
            )
        self.stdout.write(self.style.SUCCESS('Flight data successfully uploaded.'))