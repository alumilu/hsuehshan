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

#BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#TIS_DOWNLOAD_DIR = (os.path.join(BASE_DIR, 'Qos'),)

CHECK_INTERVAL = 60 #secs
URL_TISVCLOUD = "http://tisvcloud.freeway.gov.tw/"

#路段五分鐘動態資訊
TIS_ROADLEVEL5 = "roadlevel_value5.xml.gz"

    
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


class TisQos(object):

    def __init__(self):
	return

    def getFreewayQos(self, number, direction):
	if direction is 'N':
	    print "direction is N"
	elif direction is 'S':
	    print "direction is S"
