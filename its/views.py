from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.http import Http404
from rest_framework.renderers import JSONRenderer

from its import RouteCompute
from its_serializers import RouteQos, RouteQosSerializer

#from rest_framework import viewsets
#from rest_framework.response import Response
#from rest_framework.renderers import JSONRenderer

from its import RouteCompute
from its_serializers import RouteQos, RouteQosSerializer
#from models import RouteQos as modelRouteQos

# Create your views here.

#class Nf5QosViewSet(viewsets.ModelViewSet):
#    serializer_class = RouteQosSerializer
#    permission_classes = [IsAccountAdminOrReadOnly]
#    queryset = modelRouteQos.objects.all()

#    def retrive(self, request):
#	rc = RouteCompute()
#	qos = rc.getNf5Qos()
#   	serializer = RouteQosSerializer(qos)
 
#	return Response(serializer.data)

def nf5QosS(request):
    rc = RouteCompute()
    qos = rc.getNf5Qos('S')
    serializer = RouteQosSerializer(qos)
    
    return HttpResponse(JSONRenderer().render(serializer.data))

def nf5QosN(request):
    rc = RouteCompute()
    qos = rc.getNf5Qos('N')
    serializer = RouteQosSerializer(qos)
    
    return HttpResponse(JSONRenderer().render(serializer.data))

