from django.test import TestCase
from django.urls import reverse
import datetime as datetime
from rest_framework import status
from rest_framework.test import APITestCase
from .services import FlightEventService
from django.utils import timezone
from rest_framework.test import APIClient
from .models import FlightEvent
from .serializers import FlightEventSerializer, JourneySerializer

#### Test serializers
class FlightEventSerializerTest(TestCase):

    def test_serializer_outputs_correct_data(self):
        # Create a FlightEvent instance to serialize
        flight = FlightEvent.objects.create(
            flight_number="X123",
            departure_city="BUE",
            arrival_city="MAD",
            departure_datetime=timezone.make_aware(datetime.datetime(2024, 9, 12, 12, 0, 0)),
            arrival_datetime=timezone.make_aware(datetime.datetime(2024, 9, 13, 0, 0, 0))
        )

        # Serialize the model instance
        serializer = FlightEventSerializer(instance=flight)

        # Define the expected output dictionary
        expected_data = {
            'id': flight.id,
            'flight_number': "X123",
            'departure_city': "BUE",
            'arrival_city': "MAD",
            'departure_datetime': "2024-09-12T12:00:00Z",
            'arrival_datetime': "2024-09-13T00:00:00Z"
        }

        # Assert that the serializer's output matches the expected data
        self.assertEqual(serializer.data, expected_data)

    def test_serializer_validates_data(self):
        # Define sample data that should be valid
        valid_data = {
            'flight_number': "X123",
            'departure_city': "BOG",
            'arrival_city': "MAD",
            'departure_datetime': "2024-10-25T10:00:00Z",
            'arrival_datetime': "2024-10-25T11:30:00Z"
        }

        # Pass data to the serializer
        serializer = FlightEventSerializer(data=valid_data)

        # Assert that the data is valid
        self.assertTrue(serializer.is_valid())

        # Assert that the validated data matches the input
        self.assertEqual(serializer.validated_data['departure_city'], "BOG")


class JourneySerializerTest(TestCase):
    def test_journey_serializer_outputs_correct_data(self):
        # 1. Crear los datos de un viaje (ejemplo de viaje con una conexión)
        journey_data = {
            'connections': 1,
            'path': [
                {
                    'flight_number': 'X123',
                    'from': 'BUE',
                    'to': 'MAD',
                    'departure_time': '2024-09-12 12:00',
                    'arrival_time': '2024-09-13 00:00'
                },
                {
                    'flight_number': 'X1234',
                    'from': 'MAD',
                    'to': 'BOG',
                    'departure_time': '2024-09-13 02:00',
                    'arrival_time': '2024-09-13 03:00'
                }
            ]
        }

        # 2. Instanciar el JourneySerializer con los datos
        serializer = JourneySerializer(data=journey_data)

        # 3. Asegurarse de que los datos son válidos
        self.assertTrue(serializer.is_valid())

        # 4. Verificar que la salida del serializador coincide con los datos de entrada
        self.assertEqual(serializer.data, journey_data)

##### Test services
class JourneySearchTests(APITestCase):
    def test_valid_search(self):
        url = reverse('journey-search')
        params = {
            'date': '2024-09-12',
            'from': 'BUE',
            'to': 'MAD'
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_missing_parameters(self):
        url = reverse('journey-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_date_format(self):
        url = reverse('journey-search')
        params = {
            'date': '2024/09/12',
            'from': 'BUE',
            'to': 'MAD'
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class FlightSearchServiceTests(TestCase):
    def setUp(self):
        self.service = FlightEventService()

    def test_parse_datetime(self):
        dt = self.service.parse_datetime("2024-09-12T12:00:00.000Z")
        self.assertEqual(dt.year, 2024)
        self.assertEqual(dt.month, 9)
        self.assertEqual(dt.day, 12)

##### Test API
class JourneySearchAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = '/journeys/search/'

        # Create test journeys
        # Vuelo directo BUE -> MAD
        self.flight1 = FlightEvent.objects.create(
            flight_number="X123",
            departure_city="BUE",
            arrival_city="MAD",
            departure_datetime=timezone.make_aware(datetime.datetime(2024, 9, 12, 12, 0, 0)),
            arrival_datetime=timezone.make_aware(datetime.datetime(2024, 9, 13, 0, 0, 0))
        )

        # Connecting flight MAD -> BOG
        self.flight2 = FlightEvent.objects.create(
            flight_number="X1234",
            departure_city="MAD",
            arrival_city="BOG",
            departure_datetime=timezone.make_aware(datetime.datetime(2024, 9, 13, 2, 0, 0)),
            arrival_datetime=timezone.make_aware(datetime.datetime(2024, 9, 13, 3, 0, 0))
        )

        # Flight no valid - connection > 4 hours
        self.flight_bad_connection_time = FlightEvent.objects.create(
            flight_number="X12345",
            departure_city="MAD",
            arrival_city="BOG",
            departure_datetime=timezone.make_aware(datetime.datetime(2024, 9, 13, 7, 0, 0)), #
            arrival_datetime=timezone.make_aware(datetime.datetime(2024, 9, 13, 8, 0, 0))
        )

    def test_search_direct_journey(self):
        # Search direct flight BUE -> MAD
        response = self.client.get(self.base_url, {
            'date': '2024-09-12',
            'from': 'BUE',
            'to': 'MAD'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        journey = response.data[0]
        self.assertEqual(journey['connections'], 0)
        self.assertEqual(len(journey['path']), 1)
        self.assertEqual(journey['path'][0]['flight_number'], "X123")

    def test_search_journey_with_one_connection(self):
        # Search connecting flight BUE -> BOG
        response = self.client.get(self.base_url, {
            'date': '2024-09-12',
            'from': 'BUE',
            'to': 'BOG'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        journey = response.data[0]
        self.assertEqual(journey['connections'], 1)
        self.assertEqual(len(journey['path']), 2)
        self.assertEqual(journey['path'][0]['flight_number'], "X123")
        self.assertEqual(journey['path'][1]['flight_number'], "X1234")

    ##### Test no valid data #####
    def test_search_journey_exceeding_total_duration(self):
        # Flight no valid > 24 hours
        long_flight = FlightEvent.objects.create(
            flight_number="XX5555",
            departure_city="BUE",
            arrival_city="RIO",
            departure_datetime=timezone.make_aware(datetime.datetime(2024, 9, 12, 12, 0, 0)),
            arrival_datetime=timezone.make_aware(datetime.datetime(2024, 9, 13, 14, 0, 0))
        )
        response = self.client.get(self.base_url, {
            'date': '2024-09-12',
            'from': 'BUE',
            'to': 'RIO'
        })
        # Don´t shows journeys
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_search_journey_with_bad_connection_time(self):
        # Search connecting flight > 4 hours
        response = self.client.get(self.base_url, {
            'date': '2024-09-12',
            'from': 'BUE',
            'to': 'BOG'
        })
        journey = response.data[0]
        self.assertNotIn("X12345", [f['flight_number'] for f in journey['path']])

    def test_search_non_existent_journey(self):
        # Search flight doesn't exists
        response = self.client.get(self.base_url, {
            'date': '2024-09-12',
            'from': 'BUE',
            'to': 'NYC'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
