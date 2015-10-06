#!/usr/bin/python
# -*- coding: utf8 -*-

import threading
import time
import datetime
import os
import urllib2
import gzip
import StringIO
import sys
import xml.dom.minidom
import csv


from models import Current_RouteQos_Here, Current_RouteQos_Tsi 
from xml.dom.minidom import parse
from django.utils import timezone
from itertools import chain

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIS_DIR = (os.path.join(BASE_DIR, 'traffic_data'))

CHECK_INTERVAL = 300 #secs

    
class TisvCloudService(threading.Thread):

    _tis_url = 'http://tisvcloud.freeway.gov.tw/'
    _tis_roadlevel_value5 = 'roadlevel_value5.xml'
    _tis_roadlevel_info = 'roadlevel_info.xml'
    _tis_roadlevel_threshold = 'roadlevel_threshold.xml'
    _tis_route_nf5_S = {'nfb0365':'南港系統交流道到石碇交流道', 'nfb0367':'石碇交流道到坪林行控交流道', 'nfb0369':'坪林行控交流道到頭城交流道',
			'nfb0373':'頭城交流道到宜蘭交流道', 'nfb0375':'宜蘭交流道到羅東交流道', 'nfb0377':'羅東交流道到蘇澳交流道',
		       }
    _tis_route_nf5_N = {'nfb0366':'石碇交流道到南港系統交流道', 'nfb0368':'坪林行控交流道到石碇交流道', 'nfb0370':'頭城交流道到坪林行控交流道', 
			'nfb0374':'宜蘭交流道到頭城交流道', 'nfb0376':'羅東交流道到宜蘭交流道', 'nfb0378':'蘇澳交流道到羅東交流道',
		       }

    def __init__(self):
	threading.Thread.__init__(self)

    def writeDB(self):
	routes = dict(chain(TisvCloudService._tis_route_nf5_N.items(), TisvCloudService._tis_route_nf5_S.items()))
		
	roadlevel5Qos=((xml.dom.minidom.parse(os.path.join(TIS_DIR, TisvCloudService._tis_roadlevel_value5))).documentElement).getElementsByTagName('Info')

        for q in roadlevel5Qos:
	    route_id = q.getAttribute('routeid')

            if route_id in routes:
		try:
		    sec = Current_RouteQos_Tsi.objects.get(RouteId=route_id)
		    sec.Level = q.getAttribute('level')
		    sec.Speed = q.getAttribute('value') 
		    sec.TravelTime = q.getAttribute('traveltime')
		    sec.CollectTime = timezone.now()
		except Current_RouteQos_Tsi.DoesNotExist:
		    sec = Current_RouteQos_Tsi(RouteId=route_id,
					RouteName=routes[route_id],
					Level=q.getAttribute('level'),
					Speed=q.getAttribute('value'),
					TravelTime=q.getAttribute('traveltime'),
					Distance=0,
					CollectTime=timezone.now())
		finally:
		    sec.save()

	return 0


    def run(self):
	try:
	    r1 = urllib2.urlopen(TisvCloudService._tis_url + TisvCloudService._tis_roadlevel_info + '.gz')
	    r2 = urllib2.urlopen(TisvCloudService._tis_url + TisvCloudService._tis_roadlevel_threshold + '.gz')
	except:
	    #todo here
	    pass
	else:
	    b1 = StringIO.StringIO()
	    b2 = StringIO.StringIO()
	    b1.write(r1.read())
	    b2.write(r2.read())
	    b1.seek(0)
	    b2.seek(0)
	
	    df1 = gzip.GzipFile(fileobj=b1, mode='rb')
	    df2 = gzip.GzipFile(fileobj=b2, mode='rb')
	
	    with open(os.path.join(TIS_DIR, TisvCloudService._tis_roadlevel_info), 'w') as of1:
		of1.write(df1.read())

	    with open(os.path.join(TIS_DIR, TisvCloudService._tis_roadlevel_threshold), 'w') as of2:
		of2.write(df2.read())

	    b1.close()
	    b2.close()
	    df1.close()
	    df2.close()

	while(True):
	    try:
	    	response = urllib2.urlopen(TisvCloudService._tis_url + TisvCloudService._tis_roadlevel_value5 + '.gz')
	    except:
		#todo here
		pass
	    else:
	    	buf = StringIO.StringIO()
	    	buf.write(response.read())
	    	buf.seek(0)

	    	decompressFile = gzip.GzipFile(fileobj=buf, mode='rb')

		with open(os.path.join(TIS_DIR, TisvCloudService._tis_roadlevel_value5), 'w') as outfile:
		    outfile.write(decompressFile.read())

		buf.close()
		decompressFile.close()

		self.writeDB()

	    time.sleep(CHECK_INTERVAL)

    def getRouteQos(self, direction):
	qos = {}

	if direction is 'N':
            routes = TisvCloudService._tis_route_nf5_N
        elif direction is 'S':
            routes = TisvCloudService._tis_route_nf5_S
        else:
            return qos

	roadlevel5Qos = ((xml.dom.minidom.parse(os.path.join(TIS_DIR, TisvCloudService._tis_roadlevel_value5))).documentElement).getElementsByTagName('Info')

	for q in roadlevel5Qos:
            if q.getAttribute('routeid') in routes:
		qos[q.getAttribute('routeid')] = {'level':q.getAttribute('level'), 'value':q.getAttribute('value'), 'traveltime':q.getAttribute('traveltime')} 

	return qos


class HereMapService(threading.Thread):
    
    _app_id_code = 'app_id=dxxoJdEHCE9sgSpRpWw0&app_code=PbDsi8zN_DujvDV4bmNyqA'
    _route_api_url = 'https://route.cit.api.here.com/routing/7.2/calculateroute.xml?'
    _route_api_options = '&mode=fastest%3Bcar%3Btraffic%3Aenabled&'
    _route_api_departure_time = '&departure=now'
    _routes_names = ('route_nf5_s','route_nf5_n','route_t9_s','route_t9_n','route_t2_s','route_t2_n','route_t2c-t2_s','route_t2c-t2_n')
    _routes_S = {'route_nf5_s':'waypoint0=25.035518%2C121.621879&waypoint1=24.835679%2C121.790240',
		 'route_t9_s':'waypoint0=24.951872%2C121.547779&waypoint1=24.952971%2C121.633754&waypoint2=24.933685%2C121.710629&waypoint3=24.866644%2C121.773731&waypoint4=24.839287%2C121.790698',
		 'route_t2_s':'waypoint0=25.121010%2C121.825652&waypoint1=25.100490%2C121.917356&waypoint2=25.006969%2C122.003009&waypoint3=24.865277%2C121.828829',
		 'route_t2c-t2_s':'waypoint0=25.102904%2C121.735896&waypoint1=25.045789%2C121.779581&waypoint2=25.018869%2C121.933434&waypoint3=24.984089%2C121.955859&waypoint4=24.865625%2C121.829209',
	        }

    _routes_N = {'route_nf5_n':'waypoint0=24.835694%2C121.790403&waypoint1=25.035517%2C121.623341',
		 'route_t9_n':'waypoint0=24.839326%2C121.790741&waypoint1=24.86638%2C121.773928&waypoint2=24.933618%2C121.710539&waypoint3=24.951834%2C121.631983&waypoint4=24.951865%2C121.547865',
		 'route_t2_n':'waypoint0=24.865277%2C121.828829&waypoint1=25.004745%2C122.002445&waypoint2=25.099643%2C121.917105&waypoint3=25.120982%2C121.825513',
		 'route_t2c-t2_n':'waypoint0=24.865323%2C121.829037&waypoint1=24.984089%2C121.955859&waypoint2=25.018869%2C121.933434&waypoint3=25.045789%2C121.779581&waypoint4=25.102904%2C121.735896',
		}
 

    def __init__(self):
	threading.Thread.__init__(self)

    def writeDB(self, direction):
	if direction is 'N':
            routes = HereMapService._routes_N
        elif direction is 'S':
            routes = HereMapService._routes_S
        else:
            return -1
         
        for key in routes:
            summary = (((xml.dom.minidom.parse(os.path.join(TIS_DIR, 'here_' + key + '.xml'))).documentElement).getElementsByTagName('Route')[0]).getElementsByTagName('Summary')

            distance = summary[0].getElementsByTagName('Distance')[0]
	    distance = int(distance.firstChild.nodeValue)

            base_time = summary[0].getElementsByTagName('BaseTime')[0]
	    base_time = int(base_time.firstChild.nodeValue)

            traffic_time = summary[0].getElementsByTagName('TrafficTime')[0]
	    traffic_time = int(traffic_time.firstChild.nodeValue)
            #travel_time = summary[0].getElementsByTagName('TravelTime')[0]

	    jf = (float(traffic_time) - float(base_time))/float(base_time)

	    try:
	    	qos = Current_RouteQos_Here.objects.get(RouteName=key)

		qos.BaseTime = base_time
		qos.TrafficTime = traffic_time
		qos.JamFactor = jf
		qos.CollectTime = timezone.now()
	    except Current_RouteQos_Here.DoesNotExist:
		qos = Current_RouteQos_Here(RouteName=key,
					BaseTime=base_time,
					TrafficTime=traffic_time,
					Distance=distance,
					JamFactor=jf,
					CollectTime=timezone.now())
	    finally:
		qos.save()

	return 0

    def run(self):
	while(True):
	    for key in HereMapService._routes_S: #get south-direction routes
	    	try:
		    responses = urllib2.urlopen(HereMapService._route_api_url + HereMapService._routes_S[key] + HereMapService._route_api_options + HereMapService._app_id_code + HereMapService._route_api_departure_time)
	    	except:
		    #todo here
		    pass
	    	else:		
		    with open(os.path.join(TIS_DIR, 'here_' + key  + '.xml'), 'w') as outfile:
		    	outfile.write(responses.read())

		self.writeDB('S')

	    for key in HereMapService._routes_N: #get north-direction routes
		try:
		    responses = urllib2.urlopen(HereMapService._route_api_url + HereMapService._routes_N[key] + HereMapService._route_api_options +HereMapService._app_id_code + HereMapService._route_api_departure_time)
		except:
		    #todo here
		    pass
		else:
		    with open(os.path.join(TIS_DIR, 'here_' + key + '.xml'), 'w') as outfile:
			outfile.write(responses.read())

		self.writeDB('N')
	
	    time.sleep(CHECK_INTERVAL)

    def getRouteQos(self, direction):
	qos = {}

	if direction is 'N':
	    routes = HereMapService._routes_N
	elif direction is 'S':
	    routes = HereMapService._routes_S
	else:
	    return qos

	for key in routes:
	    summary = (((xml.dom.minidom.parse(os.path.join(TIS_DIR, 'here_' + key + '.xml'))).documentElement).getElementsByTagName('Route')[0]).getElementsByTagName('Summary')

	    distance = summary[0].getElementsByTagName('Distance')[0]
	    base_time = summary[0].getElementsByTagName('BaseTime')[0]
	    traffic_time = summary[0].getElementsByTagName('TrafficTime')[0]
	    travel_time = summary[0].getElementsByTagName('TravelTime')[0]

            jf = (float(traffic_time.firstChild.nodeValue) - float(base_time.firstChild.nodeValue))/float(base_time.firstChild.nodeValue)

	    qos[key] = {'Distance':distance.childNodes[0].data, 'BaseTime':base_time.childNodes[0].data, 'TrafficTime':traffic_time.childNodes[0].data, 'TravelTime':travel_time.childNodes[0].data, 'JamFactor':jf}

	return qos


class RouteCompute(object):

    def __init__(self):
	return

    def suggestRoute(self, direction):
	suggested_route = None
	best_jam_factor = 1 #road closed

	here = HereMapService()
	routes = here.getRouteQos(direction)

	#eval. current nf5 traffic condition
	if direction is 'S':
	    suggested_route = routes['route_nf5_s']
	elif direction is 'N':
	    suggested_route = routes['route_nf5_n']

	best_jam_factor = (float(suggested_route['TrafficTime']) - float(suggested_route['BaseTime'])) / float(suggested_route['BaseTime'])

	if best_jam_factor <= 0.2:
	    suggested_route['JamFactor'] = float(best_jam_factor)
            suggested_route['Route'] = 'route_nf5'  
	else:
	    for r, qos in routes.iteritems():
		if r is 'route_nf5':
		    continue
   
	        jf = (float(qos['TrafficTime']) - float(qos['BaseTime'])) / float(qos['BaseTime']) 
	    
	        if jf < best_jam_factor:
		    best_jam_factor = jf
		    suggested_route = routes[r]
		    suggested_route['JamFactor'] = float(best_jam_factor)
		    suggested_route['Route'] = r

	return suggested_route

    def getNf5Qos(self, direction):
	here = HereMapService()
	routes = here.getRouteQos(direction)
	routename = ''
	nf5 = None

	if direction is 'S':
	    nf5 = routes['route_nf5_s']
	    routename = 'Nankang to Toucheng'
	elif direction is 'N':
	    nf5 = routes['route_nf5_n']
	    routename = 'Toucheng to Nankang'

	jf = (float(nf5['TrafficTime']) - float(nf5['BaseTime'])) / float(nf5['BaseTime'])
	nf5['JamFactor'] = float(jf)

#	qos = RouteQos(routename, float(nf5['BaseTime']), float(nf5['TrafficTime']), jf, float(nf5['Distance']))
#
#	return qos
	return nf5

    def getNf5QosTisv(self, direction):
	tisv = TisvCloudService()
	nf5 = tisv.getRouteQos(direction)

	return nf5


class LogBot(threading.Thread):
    def __init__(self):
	threading.Thread.__init__(self)

    def log(self):
        rc = RouteCompute()

    	with open(os.path.join(TIS_DIR,'log.csv'), 'w') as logfile:
            fields = ['Direction', 'Time', 'JamFactor', 'BaseTime', 'TrafficTime', 'SuggestedRoute']
            writer = csv.DictWriter(logfile, fieldnames = fields)

            writer.writeheader()

            while(True):
		time.sleep(180)

                suggestedRoute = rc.suggestRoute('S')
                nf5Qos = rc.getNf5Qos('S')

                writer.writerow({'Direction':'S', 'Time':datetime.datetime.now().isoformat(), 'JamFactor':nf5Qos.JamFactor, 'BaseTime':nf5Qos.BaseTime, 'TrafficTime':nf5Qos.TrafficTime, 'SuggestedRoute':suggestedRoute})

		suggestedRoute = rc.suggestRoute('N')
		nf5Qos = rc.getNf5Qos('N')

		writer.writerow({'Direction':'N', 'Time':datetime.datetime.now().isoformat(), 'JamFactor':nf5Qos.JamFactor, 'BaseTime':nf5Qos.BaseTime, 'TrafficTime':nf5Qos.TrafficTime, 'SuggestedRoute':suggestedRoute})

    def run(self):
	self.log()


def main():
    rc = RouteCompute()

    #suggestedRoute = rc.suggestRoute('S')
    #nf5Qos = rc.getNf5Qos('S')

    print 'nf5 Tisv Qos S: %s' % str(rc.getNf5QosTisv('S'))
    print 'nf5 Tisv Qos N: %s' % str(rc.getNf5QosTisv('N'))
    print 'nf5 Qos S: %s' % str(rc.getNf5Qos('S'))
    print 'nf5 Qos N: %s' % str(rc.getNf5Qos('N'))
    print 'suggest route S: %s' % str(rc.suggestRoute('S'))
    print 'suggest route N: %s' % str(rc.suggestRoute('N')) 


if __name__ == "__main__":
    main()

