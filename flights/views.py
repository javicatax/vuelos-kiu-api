from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .services import FlightEventService, JourneySearchService

class JourneySearchView(APIView):
    def __init__(self):
        super().__init__()
        self.search_service = JourneySearchService()

    # Cache 15 minutes
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        try:
            # Get params
            date_str = request.GET.get('date')
            from_city = request.GET.get('from')
            to_city = request.GET.get('to')

            # Validations
            if not (date_str and from_city and to_city):
                return Response(
                    {'detail': 'date, from city and to city are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Search journeys
            journeys = self.search_service.search_journeys(date_str, from_city, to_city)

            return Response(journeys)

        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log del error para debugging
            print(f"Error searching journeys: {e}")
            return Response(
                {'detail': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
