#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Coder Alpha
# https://github.com/coder-alpha
#
# 

import os, sys, io, time, base64, hashlib
from __builtin__ import iter

bundle_path = os.path.join(os.getcwd().lstrip('\\\?').split('Plug-in Support')[0], 'Plug-ins', 'FMoviesPlus.bundle')
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
							'linux':{'url':'','file':'phantomjs','md5s':''}
							},
				'Cryptodome': {
							'Shared':True,
							'isFile':False,
							'local_path':modules_path,
							'win32':{'url':'','file':'Cryptodome','md5s':'306b92b4b6d5ff03bd64ec624d44e2a0'},
							'darwin':{'url':'','file':'Cryptodome','md5s':''},
							'linux':{'url':'','file':'Cryptodome','md5s':''}
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
	
	#msg = "Modules Path: %s" % modules_path
	#CHECK_ROUTINE_LOG.append(msg)
	
	for i in EXTERNALS.keys():
		if EXTERNALS[i]['Shared'] == True:
			msg = "Verifying: %s" % i
			CHECK_ROUTINE_LOG.append(msg)
			msg = "Presence: %s" % checkFilePresence(os.path.join(EXTERNALS[i]['local_path'],EXTERNALS[i][osplat]['file']), EXTERNALS[i]['isFile'])
			CHECK_ROUTINE_LOG.append(msg)
			if EXTERNALS[i][osplat]['md5s'] != '':
				md5s = md5(os.path.join(EXTERNALS[i]['local_path'],EXTERNALS[i][osplat]['file']), EXTERNALS[i]['isFile'])
				msg = "MD5 Checksum: %s | Match: %s" % (md5s, True if md5s == EXTERNALS[i][osplat]['md5s'] else False)
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