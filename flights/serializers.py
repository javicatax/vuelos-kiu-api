from rest_framework import serializers
from .models import FlightEvent

class FlightEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = FlightEvent
        fields = '__all__'

class JourneySerializer(serializers.Serializer):
    connections = serializers.IntegerField()
    # Save path as a list of dicts
    path = serializers.ListField(child=serializers.DictField())