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

#BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#TIS_DOWNLOAD_DIR = (os.path.join(BASE_DIR, 'Qos'),)

CHECK_INTERVAL = 60 #secs
URL_TISVCLOUD = "http://tisvcloud.freeway.gov.tw/"

#路段五分鐘動態資訊
TIS_ROADLEVEL5 = "roadlevel_value5.xml.gz"

FREEWAY_5_ROUTEIDS_S = ('nfb0365', 'nfb0367', 'nfb0369', 'nfb0373', 'nfb0375', 'nfb0377')
FREEWAY_5_ROUTEIDS_N = ('nfb0366', 'nfb0368', 'nfb0370', 'nfb0374', 'nfb0376', 'nfb0378')
    
class TisvcloudChecker(threading.Thread):

    def __init__(self):
	threading.Thread.__init__(self)
	
    def run(self):
	
	while(True):
	    print "Checking Tisvcloud DB..."

	    #now = datetime.datetime.now()

	    try:
	    	response = urllib2.urlopen(URL_TISVCLOUD + TIS_ROADLEVEL5)
	    except:
		#todo
		pass
	    else:
	    	buf = StringIO.StringIO()
	    	buf.write(response.read())
	    	buf.seek(0)

	    	decompressFile = gzip.GzipFile(fileobj=buf, mode='rb')

	    	with open('roadlevel_value5.xml', 'w') as outfile:
		    outfile.write(decompressFile.read())

		buf.close()
		decompressFile.close()

	    time.sleep(CHECK_INTERVAL)


class Freeway(object):

    def __init__(self):
	self.roadlevel5Qos = ((xml.dom.minidom.parse('roadlevel_value5.xml')).documentElement).getElementsByTagName('Info')
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


if __name__ == "__main__":
    main()

