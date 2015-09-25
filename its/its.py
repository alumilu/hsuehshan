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

from xml.dom.minidom import parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIS_DIR = (os.path.join(BASE_DIR, 'traffic_data'))

CHECK_INTERVAL = 300 #secs

    
class TisvCloudService(threading.Thread):

    def __init__(self):
	threading.Thread.__init__(self)

	self.tis_url = 'http://tisvcloud.freeway.gov.tw/'
	self.tis_roadlevel_value5 = 'roadlevel_value5.xml'
	self.tis_roadlevel_info = 'roadlevel_info.xml'
	self.tis_roadlevel_threshold = 'roadlevel_threshold.xml'
	self.tis_route_nf5_S = ('nfb0365', 'nfb0367', 'nfb0369', 'nfb0373', 'nfb0375', 'nfb0377')
	self.tis_route_nf5_N = ('nfb0366', 'nfb0368', 'nfb0370', 'nfb0374', 'nfb0376', 'nfb0378')
	
    def run(self):
	try:
	    r1 = urllib2.urlopen(self.tis_url + self.tis_roadlevel_info + '.gz')
	    r2 = urllib2.urlopen(self.tis_url + self.tis_roadlevel_threshold + '.gz')
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
	
	    with open(os.path.join(TIS_DIR, self.tis_roadlevel_info), 'w') as of1:
		of1.write(df1.read())

	    with open(os.path.join(TIS_DIR, self.tis_roadlevel_threshold), 'w') as of2:
		of2.write(df2.read())

	    b1.close()
	    b2.close()
	    df1.close()
	    df2.close()

	while(True):
	    try:
	    	response = urllib2.urlopen(self.tis_url + self.tis_roadlevel_value5 + '.gz')
	    except:
		#todo here
		pass
	    else:
	    	buf = StringIO.StringIO()
	    	buf.write(response.read())
	    	buf.seek(0)

	    	decompressFile = gzip.GzipFile(fileobj=buf, mode='rb')

		with open(os.path.join(TIS_DIR, self.tis_roadlevel_value5), 'w') as outfile:
		    outfile.write(decompressFile.read())

		buf.close()
		decompressFile.close()

	    time.sleep(CHECK_INTERVAL)

    def getRouteQos(self, direction):
	qos = {}

	if direction is 'N':
            routes = self.tis_route_nf5_N
        elif direction is 'S':
            routes = self.tis_route_nf5_S
        else:
            return qos

	roadlevel5Qos = ((xml.dom.minidom.parse(os.path.join(TIS_DIR, self.tis_roadlevel_value5))).documentElement).getElementsByTagName('Info')

	for q in roadlevel5Qos:
            if q.getAttribute('routeid') in routes:
		qos[q.getAttribute('routeid')] = {'level':q.getAttribute('level'), 'value':q.getAttribute('value'), 'traveltime':q.getAttribute('traveltime')} 

	return qos


class HereMapService(threading.Thread):
    
    def __init__(self):
	threading.Thread.__init__(self)

	self.app_id_code = 'app_id=dxxoJdEHCE9sgSpRpWw0&app_code=PbDsi8zN_DujvDV4bmNyqA'
	self.route_api_url = 'https://route.cit.api.here.com/routing/7.2/calculateroute.xml?'
	self.route_api_options = '&mode=fastest%3Bcar%3Btraffic%3Aenabled&'
	self.route_api_departure_time = '&departure=now'
	self.routes_S = {'route_nf1-ex62-t2':'waypoint0=25.074163%2C121.654351&waypoint1=25.105115%2C121.732100&waypoint2=25.119496%2C121.894320&waypoint3=25.102189%2C121.918021&waypoint4=25.016880%2C121.941833&waypoint5=24.868920%2C121.831650',
		       'route_nf3a-nf3-nf5':'waypoint0=25.004415%2C121.580521&waypoint1=25.034974%2C121.623374&waypoint2=24.830491%2C121.790767',
		      }
	self.routes_N ={}

    def run(self):
	while(True):
	    for key in self.routes_S: #get south-direction routes
	    	try:
		    responses = urllib2.urlopen(self.route_api_url + self.routes_S[key] + self.route_api_options + self.app_id_code + self.route_api_departure_time)
	    	except:
		    #todo here
		    pass
	    	else:		
		    with open(os.path.join(TIS_DIR, 'here_' + key  + '.xml'), 'w') as outfile:
		    	outfile.write(responses.read())

	    for key in self.routes_N: #get north-direction routes
		try:
		    responses = urllib2.urlopen(self.route_api_url + self.routes_N[key] + self.route_api_options + self.app_id_code + self.route_api_departure_time)
		except:
		    #todo here
		    pass
		else:
		    with open(os.path.join(TIS_DIR, 'here_' + key + '.xml'), 'w') as outfile:
			outfile.write(responses.read())
	
	    time.sleep(CHECK_INTERVAL)

    def getRouteQos(self, direction):
	qos = {}

	if direction is 'N':
	    routes = self.routes_N
	elif direction is 'S':
	    routes = self.routes_S
	else:
	    return qos

	for key in routes:
	    summary = (((xml.dom.minidom.parse(os.path.join(TIS_DIR, 'here_' + key + '.xml'))).documentElement).getElementsByTagName('Route')[0]).getElementsByTagName('Summary')

	    distance = summary[0].getElementsByTagName('Distance')[0]
	    base_time = summary[0].getElementsByTagName('BaseTime')[0]
	    traffic_time = summary[0].getElementsByTagName('TrafficTime')[0]
	    travel_time = summary[0].getElementsByTagName('TravelTime')[0]

	    qos[key] = {'Distance':distance.childNodes[0].data, 'BaseTime':base_time.childNodes[0].data, 'TrafficTime':traffic_time.childNodes[0].data, 'TravelTime':travel_time.childNodes[0].data}
		

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
	suggested_route = routes['route_nf3a-nf3-nf5']
	best_jam_factor = (float(suggested_route['TrafficTime']) - float(suggested_route['BaseTime'])) / float(suggested_route['BaseTime'])

	if best_jam_factor <= 0.2:
	    suggested_route['JamFactor'] = float(best_jam_factor)
            suggested_route['Route'] = 'route_nf3a-nf3-nf5'  
	else:
	    for r, qos in routes.iteritems():
		if r is 'route_nf3a-nf3-nf5':
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
	nf5 = routes['route_nf3a-nf3-nf5']

	jf = (float(nf5['TrafficTime']) - float(nf5['BaseTime'])) / float(nf5['BaseTime'])
	nf5['JamFactor'] = float(jf)

	return nf5

import csv

class LogBot(object):
    def __init__(self):
	return

    def log(self):
         rc = RouteCompute()

    	 with open(os.path.join(TIS_DIR,'log.csv'), 'aw') as logfile:
             fields = ['Time', 'JamFactor', 'BaseTime', 'TrafficTime', 'SuggestedRoute']
             writer = csv.DictWriter(logfile, fieldnames = fields)

             writer.writeheader()

             while(True):
                 suggestedRoute = rc.suggestRoute('S')
                 nf5Qos = rc.getNf5Qos('S')

                 writer.writerow({'Time':datetime.datetime.now().isoformat(), 'JamFactor':nf5Qos['JamFactor'], 'BaseTime':nf5Qos['BaseTime'], 'TrafficTime':nf5Qos['TrafficTime'], 'SuggestedRoute':suggestedRoute})
            	 time.sleep(60)


def main():
    rc = RouteCompute()

    with open ('log.csv', 'aw') as logfile:
	fields = ['Time', 'JamFactor', 'BaseTime', 'TrafficTime', 'SuggestedRoute']
	writer = csv.DictWriter(logfile, fieldnames = fields)
	
	writer.writeheader()

	while(True):
	    suggestedRoute = rc.suggestRoute('S')
	    nf5Qos = rc.getNf5Qos('S')

	    writer.writerow({'Time':datetime.datetime.now().isoformat(), 'JamFactor':nf5Qos['JamFactor'], 'BaseTime':nf5Qos['BaseTime'], 'TrafficTime':nf5Qos['TrafficTime'], 'SuggestedRoute':suggestedRoute})
	    time.sleep(30)
    


if __name__ == "__main__":
    main()

