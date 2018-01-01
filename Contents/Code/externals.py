#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Coder Alpha
# https://github.com/coder-alpha
#
# 

import os, sys, io, time, base64, hashlib
import common
from __builtin__ import iter

plugins_path = os.getcwd().lstrip('\\\?').split('Plug-in Support')[0]
if 'Plug-ins' in plugins_path:
	plugins_path = plugins_path.split('Plug-ins')[0]
bundle_path = os.path.join(plugins_path, 'Plug-ins', 'FMoviesPlus.bundle')
modules_path = os.path.join(bundle_path, 'Contents', 'Libraries', 'Shared')

BUSY_BOOL = []
CHECK_ROUTINE_LOG = []

EXTERNALS = {
				'PhantomJS': {
							'Shared':True,
							'isFile':True,
							'local_path':os.path.join(modules_path,'phantomjs'),
							'win32':{'url':'','file':'phantomjs.exe','md5s':'339f74c735e683502c43512a508e53d6'},
							'darwin':{'url':'','file':'phantomjs','md5s':''},
							'linux':{'url':'','file':'phantomjs','md5s':'0a6c36ddd62eee77a015d0592e009ce9'},
							'linux2':{'url':'','file':'phantomjs','md5s':'0a6c36ddd62eee77a015d0592e009ce9'},
							'freebsd9':{'url':'','file':'phantomjs','md5s':'c95484f0719e1cbbb39255316eea1997'},
							'generic':{'url':'','file':'phantomjs','md5s':''}
							},
				'Cryptodome': {
							'Shared':True,
							'isFile':False,
							'local_path':modules_path,
							'win32':{'url':'','file':'Cryptodome','md5s':'306b92b4b6d5ff03bd64ec624d44e2a0'},
							'darwin':{'url':'','file':'Cryptodome','md5s':''},
							'linux':{'url':'','file':'Cryptodome','md5s':'3ee42aceb7618051ebc62bfaa5c20604'},
							'linux2':{'url':'','file':'Cryptodome','md5s':'3ee42aceb7618051ebc62bfaa5c20604'},
							'freebsd9':{'url':'','file':'Cryptodome','md5s':''},
							'generic':{'url':'','file':'Cryptodome','md5s':''}
							},
				'USS': 		{
							'Shared':False,
							'local_path':'',
							'os':{'url':'','md5s':''}
							}
			}

def checkRoutine():
	
	BUSY_BOOL.append(True)
	del CHECK_ROUTINE_LOG[:]
	
	osplat = sys.platform
	
	msg = "OS/Platform: %s" % osplat
	CHECK_ROUTINE_LOG.append(msg)
	
	msg = "Modules Path: %s" % modules_path
	#CHECK_ROUTINE_LOG.append(msg)
	#print msg
	
	for i in EXTERNALS.keys():
		if EXTERNALS[i]['Shared'] == True:
			msg = "Verifying: %s" % i
			CHECK_ROUTINE_LOG.append(msg)
			
			DIR_PATH = EXTERNALS[i]['local_path']
			
			if i == 'PhantomJS':
				USER_DEFINED_PATH = common.control.setting('control_phantomjs_path')
				if USER_DEFINED_PATH != None and len(USER_DEFINED_PATH) > 0:
					DIR_PATH = USER_DEFINED_PATH
				
			if osplat not in EXTERNALS[i].keys():
				msg = "OS/Platform not defined in externals.py - trying 'generic'"
				CHECK_ROUTINE_LOG.append(msg)
				osplat = 'generic'
				
			try:
				msg = "Path: %s" % os.path.join(DIR_PATH,EXTERNALS[i][osplat]['file'])
			except Exception as e:
				msg = "ERROR externals.py>: Path listing caused an error: %s" % e
			CHECK_ROUTINE_LOG.append(msg)
			
			try:
				msg = "Presence: %s" % checkFilePresence(os.path.join(DIR_PATH,EXTERNALS[i][osplat]['file']), EXTERNALS[i]['isFile'])
			except Exception as e:
				msg = "ERROR externals.py>: Presence check routine caused an error: %s" % e
			CHECK_ROUTINE_LOG.append(msg)

			try:
				md5s = md5(os.path.join(DIR_PATH,EXTERNALS[i][osplat]['file']), EXTERNALS[i]['isFile'])
				if EXTERNALS[i][osplat]['md5s'] != '':
					msg = "MD5 Checksum: %s | Match: %s" % (md5s, True if md5s == EXTERNALS[i][osplat]['md5s'] else False)
				else:
					msg = "MD5 Checksum: %s | Match: %s" % (md5s, 'Unknown')
			except Exception as e:
				msg = "ERROR externals.py>: MD5 Checksum routine caused an error: %s" % e
			CHECK_ROUTINE_LOG.append(msg)
			
	del BUSY_BOOL[:]
			
def checkFilePresence(binary_path, isFile):
	try:
		if isFile == True:
			if os.path.isfile(binary_path):
				return True
		else:
			if os.path.isdir(binary_path):
				return True
	except:
		pass
	return False
			
			
def md5(fname, isFile):
	if isFile == True:
		return md5File(fname)
	else:
		return md5Dir(fname)
			
def md5File(fname):
	try:
		SHAhash = hashlib.md5()
		with io.open(fname, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				SHAhash.update(chunk)
		return SHAhash.hexdigest()
	except:
		return '0'
		
def md5Dir(directory):
	try:
		SHAhash = hashlib.md5()
		for root, dirs, files in os.walk(directory):
			for names in files:
				if ('.py' in names or '.pyd' in names) and '.pyc' not in names:
					filepath = os.path.join(root,names)
					try:
						f1 = io.open(filepath, 'rb')
					except:
						# You can't open the file for some reason
						f1.close()
						continue
					while 1:
						# Read file in as little chunks
						buf = f1.read(4096)
						if not buf : break
						SHAhash.update(hashlib.md5(buf).hexdigest())
					f1.close()
		return SHAhash.hexdigest()
	except:
		pass
	return '0'
	
def test():
	checkRoutine()
	if len(CHECK_ROUTINE_LOG) > 0:
		for i in CHECK_ROUTINE_LOG:
			print i
	
#test()