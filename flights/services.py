import requests
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from django.db import transaction
from .models import FlightEvent
from django.utils import timezone

class FlightEventService:
    MOCK_API_URL = "https://mock.apidog.com/m1/814105-793312-default/flight-events"

    @staticmethod
    def parse_datetime(dt_str: str) -> datetime:
        """Parse datetime from ISO format"""
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Format datetime to required format"""
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def is_validate_flight_event(self, event_data: Dict) -> bool:
        """Validate flight event data"""
        required_fields = [
            'flight_number', 'departure_city', 'arrival_city',
            'departure_datetime', 'arrival_datetime'
        ]

        if not all(field in event_data for field in required_fields):
            return False

        # Validate datetime formats
        try:
            dep_dt = self.parse_datetime(event_data['departure_datetime'])
            arr_dt = self.parse_datetime(event_data['arrival_datetime'])

            if arr_dt <= dep_dt:
                return False

        except (ValueError, TypeError):
            return False

        # Validate city codes (3 letters)
        if (len(event_data['departure_city']) != 3 or
                len(event_data['arrival_city']) != 3):
            return False

    ###### Save flight event
    @transaction.atomic
    def save_flight_events(self, events_data: List[Dict]) -> int:
        """
        Save multiple flight event to database
        """
        saved_flight_events = 0

        for event_data in events_data:
            if not self.is_validate_flight_event(event_data):
                continue

            try:
                flight_event, created = FlightEvent.objects.get_or_create(
                    flight_number=event_data['flight_number'],
                    departure_datetime=self.parse_datetime(event_data['departure_datetime']),
                    defaults={
                        'departure_city': event_data['departure_city'].upper(),
                        'arrival_city': event_data['arrival_city'].upper(),
                        'arrival_datetime': self.parse_datetime(event_data['arrival_datetime'])
                    }
                )

                if created:
                    saved_flight_events += 1
                else:
                    # Update existing record
                    flight_event.departure_city = event_data['departure_city'].upper()
                    flight_event.arrival_city = event_data['arrival_city'].upper()
                    flight_event.arrival_datetime = self.parse_datetime(event_data['arrival_datetime'])
                    flight_event.save()

            except Exception as e:
                print(f"Error saving flight event {event_data['flight_number']}: {e}")
                continue

        return saved_flight_events

class JourneySearchService:
    MAX_CONNECTION_HOURS = 4
    MAX_TOTAL_HOURS = 24

    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """Parse YYYY-MM-DD string to date object"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None

    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Format datetime to required string format"""
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def find_connecting_flights(self, first_leg: FlightEvent, to_city: str, results: List[Dict]):
        """Find connecting flights"""

        # Calculate start and end connection
        connection_start = first_leg.arrival_datetime
        connection_end = connection_start + timedelta(hours=self.MAX_CONNECTION_HOURS)

        # Search connecting flights
        second_legs = FlightEvent.objects.filter(
            departure_city=first_leg.arrival_city,
            departure_datetime__gte=connection_start,
            departure_datetime__lte=connection_end,
            arrival_city=to_city.upper()
        ).order_by('departure_datetime')

        for second_leg in second_legs:
            total_duration = second_leg.arrival_datetime - first_leg.departure_datetime
            if total_duration <= timedelta(hours=self.MAX_TOTAL_HOURS):
                results.append(self.journey_response([first_leg, second_leg], connections=1))

    def get_available_destinations(self, from_city: str, date_str: str) -> List[str]:
        """Get available destinations for a specific date and city"""
        date = self.parse_date(date_str)
        if date is None:
            return []

        start = timezone.datetime(date.year, date.month, date.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)

        destinations = FlightEvent.objects.filter(
            departure_city=from_city.upper(),
            departure_datetime__gte=start,
            departure_datetime__lt=end
        ).values_list('arrival_city', flat=True).distinct()

        return list(destinations)

    def get_departure_times(self, from_city: str, to_city: str, date_str: str) -> List[datetime]:
        """Get departure times for a specific date and city"""
        date = self.parse_date(date_str)
        if date is None:
            return []

        start = timezone.datetime(date.year, date.month, date.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)

        departure_times = FlightEvent.objects.filter(
            departure_city=from_city.upper(),
            arrival_city=to_city.upper(),
            departure_datetime__gte=start,
            departure_datetime__lt=end
        ).values_list('departure_datetime', flat=True).order_by('departure_datetime')

        return list(departure_times)

    def search_journeys(self, date_str: str, from_city: str, to_city: str) -> List[Dict]:
        """Search for journeys between two cities and date"""

        # Validate data
        date = self.parse_date(date_str)
        if date is None:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

        if not from_city or not to_city or len(from_city) != 3 or len(to_city) != 3:
            raise ValueError("City codes must be 3 letters")

        # Convert a datetime timezone UTC
        start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end = start + timedelta(days=1)

        # First leg connection
        first_legs = FlightEvent.objects.filter(
            departure_city=from_city.upper(),
            departure_datetime__gte=start,
            departure_datetime__lt=end
        ).order_by('departure_datetime')

        results = []

        for first_leg in first_legs:
            # Direct flight
            if first_leg.arrival_city == to_city.upper():
                total_duration = first_leg.arrival_datetime - first_leg.departure_datetime
                if total_duration <= timedelta(hours=self.MAX_TOTAL_HOURS):
                    results.append(self.journey_response([first_leg], connections=0))

            # connecting flight
            self.find_connecting_flights(first_leg, to_city, results)

        # Order by departure_time
        results.sort(key=lambda x: x['path'][0]['departure_time'])

        return results

    def journey_response(self, legs: List[FlightEvent], connections: int) -> Dict:
        """Journey response """
        return {
            'connections': connections,
            'path': [
                {
                    'flight_number': leg.flight_number,
                    'from': leg.departure_city,
                    'to': leg.arrival_city,
                    'departure_time': self.format_datetime(leg.departure_datetime),
                    'arrival_time': self.format_datetime(leg.arrival_datetime),
                }
                for leg in legs
            ]
        }