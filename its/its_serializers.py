from rest_framework import serializers
from models import Current_RouteQos_Here, Current_RouteQos_Tsi


class HereRouteQosSerializer(serializers.ModelSerializer):
    class Meta:
	model = Current_RouteQos_Here
	fields = ('RouteName', 'BaseTime','TrafficTime','JamFactor','Distance','CollectTime')


class TsiRouteQosSerializer(serializers.ModelSerializer):
    class Meta:
	model = Current_RouteQos_Tsi
	fields = ('RouteId', 'RouteName', 'Level', 'Speed', 'Distance', 'TravelTime', 'CollectTime')
