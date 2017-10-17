#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import subprocess


__title__ = "phantomjs"
__version__ = "0.0.1"
__credits__ = [
    "Coder Alpha"
]

def decode(url, python_dir=None, debug=False):
	output = ""
	try:
		PHANTOMJS_PATH = os.path.dirname(os.path.abspath(__file__))
		
		if python_dir == None:
			python_dir = ""
		
		if debug:
			if sys.platform == "win32":
				file_cmd = [os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url, '-debug true']
			elif sys.platform == "darwin":
				file_cmd = [os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url]
			else:
				file_cmd = ['xvfb-run', python_dir, os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url]
		else:
			if sys.platform == "win32":
				file_cmd = [os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url]
			elif sys.platform == "darwin":
				file_cmd = [os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url]
			else:
				file_cmd = ['xvfb-run', python_dir, os.path.join(PHANTOMJS_PATH, 'phantomjs'), os.path.join(PHANTOMJS_PATH, 'openload.js'), url]


		output = ""
		if sys.platform == "darwin":
			#print file_cmd
			process = subprocess.Popen(file_cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
			output = process.stdout.read()
		else:
			#print file_cmd
			process = subprocess.Popen(file_cmd, shell=False, cwd=PHANTOMJS_PATH, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			ret = process.wait()
			#print('Process returned code {0}'.format(ret))
			output = process.stdout.read()

		output = output.strip().replace('\n','').encode('utf8').decode('ascii')
		if 'http' in output:
			return output, True
		return output, False
	except Exception as err:
		print "phantomjs-Error: " + str(err) + " " + str(output) + " " + str(file_cmd)
		return str(err), False

def test():
	resp = decode("https://openload.co/embed/kUEfGclsU9o", debug=False)
	print resp[0]
	
#test()
