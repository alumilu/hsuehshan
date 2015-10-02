from rest_framework import serializers   


class RouteQos(object):
    def __init__(self, routename, basetime, traffictime, jamfactor):
        self.BaseTime = basetime
        self.TrafficTime = traffictime
        self.JamFactor = jamfactor
        self.RouteName = routename
    
    
class RouteQosSerializer(serializers.Serializer):
        RouteName = serializers.CharField(max_length=64)
        BaseTime = serializers.DecimalField(max_digits=6, decimal_places=0)
        TrafficTime = serializers.DecimalField(max_digits=6, decimal_places=0)
        JamFactor = serializers.FloatField()

