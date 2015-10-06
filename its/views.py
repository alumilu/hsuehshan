#from django.shortcuts import render
#from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.db.models import Q

#from its import RouteCompute
from its_serializers import HereRouteQosSerializer, TsiRouteQosSerializer
from models import Current_RouteQos_Here, Current_RouteQos_Tsi

#from rest_framework import viewsets
#from rest_framework.response import Response


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

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def RouteQosList(request):
    if request.method == 'GET':
	qos = Current_RouteQos_Here.objects.all()
        serializer = HereRouteQosSerializer(qos, many=True)
        return JSONResponse(serializer.data)

def nf5QosS(request):
    if request.method == 'GET':
	qos = Current_RouteQos_Here.objects.get(RouteName='route_nf5_s')
	serializer = HereRouteQosSerializer(qos)
	return JSONResponse(serializer.data)

def nf5QosN(request):
    if request.method == 'GET':
        qos = Current_RouteQos_Here.objects.get(RouteName='route_nf5_n')
        serializer = HereRouteQosSerializer(qos)
        return JSONResponse(serializer.data)

def nf5SectionQosS(request):
    if request.method == 'GET':
	qos = Current_RouteQos_Tsi.objects.all().filter(Q(RouteId='nfb0365')|Q(RouteId='nfb0367')|Q(RouteId='nfb0369')|Q(RouteId='nfb0373')|Q(RouteId='nfb0375')|Q(RouteId='nfb0377'))
	serializer = TsiRouteQosSerializer(qos, many=True)
        return JSONResponse(serializer.data)

def nf5SectionQosN(request):
    if request.method == 'GET':        
	qos = Current_RouteQos_Tsi.objects.all().filter(Q(RouteId='nfb0366')|Q(RouteId='nfb0368')|Q(RouteId='nfb0370')|Q(RouteId='nfb0374')|Q(RouteId='nfb0376')|Q(RouteId='nfb0378'))
        serializer = TsiRouteQosSerializer(qos, many=True)
        return JSONResponse(serializer.data)

