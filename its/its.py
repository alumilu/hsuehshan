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
TIS_DIR = (os.path.join(BASE_DIR, 'freeway.gov.db'))

CHECK_INTERVAL = 300 #secs
URL_TISVCLOUD = "http://tisvcloud.freeway.gov.tw/"

TIS_ROADLEVEL_VALUE5 = "roadlevel_value5.xml"
TIS_ROADLEVEL_INFO = "roadlevel_info.xml"
TIS_ROADLEVEL_THRESHOLD = "roadlevel_threshold.xml"

FREEWAY_5_ROUTEIDS_S = ('nfb0365', 'nfb0367', 'nfb0369', 'nfb0373', 'nfb0375', 'nfb0377')
FREEWAY_5_ROUTEIDS_N = ('nfb0366', 'nfb0368', 'nfb0370', 'nfb0374', 'nfb0376', 'nfb0378')
    
class TisvcloudChecker(threading.Thread):

    def __init__(self):
	threading.Thread.__init__(self)
	
    def run(self):
	
	try:
	    print "updating freeway info and threshold data..."
	    r1 = urllib2.urlopen(URL_TISVCLOUD + TIS_ROADLEVEL_INFO + '.gz')
	    r2 = urllib2.urlopen(URL_TISVCLOUD + TIS_ROADLEVEL_THRESHOLD + '.gz')
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
	
	    with open(os.path.join(TIS_DIR, TIS_ROADLEVEL_INFO), 'w') as of1:
		of1.write(df1.read())

	    with open(os.path.join(TIS_DIR, TIS_ROADLEVEL_THRESHOLD), 'w') as of2:
		of2.write(df2.read())

	    b1.close()
	    b2.close()
	    df1.close()
	    df2.close()

	while(True):

	    print "updating freeway realtime traffic conditions..."

	    try:
	    	response = urllib2.urlopen(URL_TISVCLOUD + TIS_ROADLEVEL_VALUE5 + '.gz')
	    except:
		#todo here
		pass
	    else:
	    	buf = StringIO.StringIO()
	    	buf.write(response.read())
	    	buf.seek(0)

	    	decompressFile = gzip.GzipFile(fileobj=buf, mode='rb')

		with open(os.path.join(TIS_DIR, TIS_ROADLEVEL_VALUE5), 'w') as outfile:
		    outfile.write(decompressFile.read())

		buf.close()
		decompressFile.close()

	    time.sleep(CHECK_INTERVAL)


class HerePlatform(threading.Thread):
    
    def __init__(self):
	threading.Thread.__init__(self)

	self.app_id_code = 'app_id=dxxoJdEHCE9sgSpRpWw0&app_code=PbDsi8zN_DujvDV4bmNyqA'
	self.route_api_url = 'https://route.cit.api.here.com/routing/7.2/calculateroute.xml?'
	self.route_api_options = '&mode=fastest%3Bcar%3Btraffic%3Aenabled&'
	self.route_api_departure_time = '&departure=now'
	self.routes = {'test':'waypoint0=25.060272%2C121.647702&waypoint1=24.893166%2C121.194685',}


    def run(self):

	while(True):
	    
	    print 'updating here traffic conditions...'

	    try:
		responses = urllib2.urlopen(self.route_api_url + self.routes['test'] + self.route_api_options + self.app_id_code + self.route_api_departure_time)
	    except:
		#todo here
		pass
	    else:		
		with open(os.path.join(TIS_DIR, 'here_test_route.xml'), 'w') as outfile:
		    outfile.write(responses.read())
	
	    time.sleep(CHECK_INTERVAL)

    def getQos(self):
	qos = {}

	return qos


class Freeway(object):

    def __init__(self):
	self.roadlevel5Qos = ((xml.dom.minidom.parse(os.path.join(TIS_DIR, TIS_ROADLEVEL_VALUE5))).documentElement).getElementsByTagName('Info')
	return

    def getQos(self, number, direction, start_section='', end_section=''):

	qos = {}

	if number is 5:
	    if direction is 'N':
		routeids = FREEWAY_5_ROUTEIDS_N
	    elif direction is 'S':
		routeids = FREEWAY_5_ROUTEIDS_S

	    for q in self.roadlevel5Qos:
		if q.getAttribute('routeid') in routeids:
		    qos[q.getAttribute('routeid')] = {'level':q.getAttribute('level'), 'value':q.getAttribute('value'), 'traveltime':q.getAttribute('traveltime')} 

	return qos


def main():
    freeway = Freeway()

    qos = freeway.getQos(5, 'N')
    print str(qos)

    print os.path.join(TIS_DIR, TIS_ROADLEVEL_VALUE5)


if __name__ == "__main__":
    main()

