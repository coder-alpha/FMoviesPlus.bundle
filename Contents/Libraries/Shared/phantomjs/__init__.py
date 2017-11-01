#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, time, base64
import subprocess

try:
	PATH_R = os.path.dirname(os.path.abspath(__file__)).split('Shared')[0]
except:
	PATH_R = os.path.dirname(os.path.abspath('__file__')).split('Shared')[0]

PATH = os.path.join(PATH_R, 'Shared/resources/lib/libraries')
sys.path.insert(0,PATH)

import control

__title__ = "phantomjs"
__version__ = "0.0.1"
__credits__ = [
    "Coder Alpha"
]

PROCESSES = {}

def decode(url, python_dir=None, debug=False, ssl=True):
	output = ""
	try:
		url_encode = base64.b64encode(url)
		PHANTOMJS_PATH = os.path.dirname(os.path.abspath(__file__))
		
		if python_dir == None:
			python_dir = ""
		
		if debug:
			if sys.platform == "win32":
				file_cmd = [os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url, '-debug true']
			elif sys.platform == "darwin":
				file_cmd = [os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url]
			else:
				file_cmd = [os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url]
		else:
			if sys.platform == "win32":
				file_cmd = [os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url]
			elif sys.platform == "darwin":
				file_cmd = [os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url]
			else:
				file_cmd = [os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url]

		if ssl == True:
			file_cmd.insert(1,'--ssl-protocol=any')

		output = ""
		if sys.platform == "darwin":
			#print file_cmd
			PROCESSES[url_encode] = {'url':url,'ts':time.time(),'Completed':False}
			process = subprocess.Popen(file_cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
			PROCESSES[url_encode].update({'process':process})
			ret = process.wait()
			output = process.stdout.read()
			PROCESSES[url_encode].update({'output':output})
		else:
			#print file_cmd
			PROCESSES[url_encode] = {'url':url,'ts':time.time(),'Completed':False}
			process = subprocess.Popen(file_cmd, shell=False, cwd=PHANTOMJS_PATH, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			PROCESSES[url_encode].update({'process':process})
			ret = process.wait()	
			output = process.stdout.read()
			PROCESSES[url_encode].update({'output':output})

		output = output.strip().replace('\n','').encode('utf8').decode('ascii')
		PROCESSES[url_encode].update({'Completed':True})

		if 'http' in output:
			return output, True
		return output, False
	except Exception as err:
		log(type='ERROR', err= "%s > %s > %s" % (str(err), str(output), str(file_cmd)))
		return str(err), False

def log(err='', type='INFO', logToControl=True):
	try:
		msg = '%s: %s > %s : %s' % (time.ctime(time.time()), type, 'PhantomJS', err)
		if dolog == True:
			loggertxt.append(msg)
		if logToControl == True:
			control.log(msg)
		if control.doPrint == True and doPrint == True:
			print msg
	except Exception as e:
		control.log('Error in Logging: %s >>> %s' % (msg,e))
		
def test():
	resp = decode("https://openload.co/embed/kUEfGclsU9o", debug=False)
	print resp[0]
	log(PROCESSES)
	
#test()
