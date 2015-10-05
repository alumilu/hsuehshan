from rest_framework import serializers


class RouteQos(object):
    def __init__(self, routename, basetime, traffictime, jamfactor, distance):
        self.BaseTime = basetime
        self.TrafficTime = traffictime
        self.JamFactor = jamfactor
        self.RouteName = routename
	self.Distance = distance
    
    
class RouteQosSerializer(serializers.Serializer):
        RouteName = serializers.CharField(max_length=64)
        BaseTime = serializers.FloatField()
        TrafficTime = serializers.FloatField()
        JamFactor = serializers.FloatField()
	Distance = serializers.FloatField()

