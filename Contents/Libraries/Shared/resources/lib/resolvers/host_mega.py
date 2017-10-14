#! /usr/bin/python
# -*- coding: utf-8 -*-

#########################################################################################################
#
# Mega scrapper
#
# Coder Alpha
# https://github.com/coder-alpha
#

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
#########################################################################################################

# by pts@fazekas.hu at Tue Oct 11 13:12:47 CEST 2016
# Modified by 
# Coder Alpha
# https://github.com/coder-alpha

""":" #megapubdl: Download public files from MEGA (mega.nz).

type python2.7 >/dev/null 2>&1 && exec python2.7 -- "$0" ${1+"$@"}
type python2.6 >/dev/null 2>&1 && exec python2.6 -- "$0" ${1+"$@"}
type python2.5 >/dev/null 2>&1 && exec python2.5 -- "$0" ${1+"$@"}
type python2.4 >/dev/null 2>&1 && exec python2.4 -- "$0" ${1+"$@"}
exec python -- ${1+"$@"}; exit 1

megapubdl is command-line tool for Unix implemented as a Python script to
download public files (with a public URL) from MEGA (mega.nz, mega.co.nz).
It works with Python 2.6 and 2.7, and needs only the `openssl' external tool or
PyCryptodome (https://github.com/Legrandin/pycryptodome) installed.

megapubdl doesn't work with Python 3.x. It works with Python 2.4
and 2.5 if the ssl module (https://pypi.python.org/pypi/ssl) is installed.

Usage:

  megapubdl.py "https://mega.nz/#!..."
"""

#
# TODO(pts): Improve error handling (especially socket errors and parse errors).
#

import base64
import urllib  # For urlencode.
import httplib
import os
import random
import re
import select
import socket
import stat
import struct
import subprocess
import sys
import traceback
import json
import ast
import urllib2,HTMLParser,urlparse
import time, cookielib

from __builtin__ import eval

try:
	from resources.lib.libraries import client
	from resources.lib.libraries import control
except:
	pass
	
crypto_msg = None
try:
	from resources.lib.libraries import mega
	mega.fix_ssl()
	print 'Cryptodome library loaded'
except:
	crypto_msg = 'Cryptodome library not found.'
	print crypto_msg

http_hdrs = {
	'User-Agent': client.USER_AGENT,
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}
	
name = 'mega'
	
class host:
	def __init__(self):
		self.logo = 'https://i.imgur.com/FYtin8g.png'
		self.name = name
		self.host = ['mega.nz','mega.co.nz']
		self.netloc = ['mega.nz']
		self.quality = '1080p'
		self.loggertxt = []
		self.captcha = False
		self.allowsDownload = True
		self.resumeDownload = False
		self.allowsStreaming = False
		self.ac = False
		self.pluginManagedPlayback = True
		self.speedtest = 0
		self.working = self.test()[0]
		self.resolver = self.test2()
		self.msg = ''
		if crypto_msg != None:
			logger('Cryptodome library not found.')
			self.msg = 'Cryptodome library not found.'
			self.resolver = False
			self.working = False
	
		#raise ValueError('Cryptodome.Cipher.AES not found.')

	def info(self):
		return {
			'name': self.name,
			'class': self.name,
			'speed': round(self.speedtest,3),
			'netloc': self.netloc,
			'host': self.host,
			'quality': self.quality,
			'logo': self.logo,
			'working': self.working,
			'resolver': self.resolver,
			'captcha': self.captcha,
			'msg': self.msg,
			'playbacksupport': self.pluginManagedPlayback,
			'a/c': self.ac,
			'streaming' : self.allowsStreaming,
			'downloading' : self.allowsDownload
		}
		
	def log(self, type, method, err, dolog=False, disp=True):
		msg = '%s : %s>%s - : %s' % (type, self.name, method, err)
		if dolog == True:
			self.loggertxt.append(msg)
		if disp == True:
			logger(msg)
		
	def test(self):
		try:
			testUrls = self.testUrl()
			bool = False
			msg = []
			for testUrl in testUrls:
				x1 = time.time()
				bool = check(testUrl)
				self.speedtest = time.time() - x1
				msg.append([bool, testUrl])
			return (bool,msg)
		except:
			return False
			
	def test2(self):
		try:
			testUrls = self.testUrl()
			links = []
			for testUrl in testUrls:
				links = self.createMeta(testUrl, 'Test', '', '', links, 'testing', 'BRRIP')
				print links
			if len(links) > 0:
				return True
		except Exception as e:
			self.log('ERROR', 'test2', e, dolog=True)
		return False
		
	def testUrl(self):
		return ['https://mega.nz/#!R6xyBBpY!JmZlf7cn7w2scbWaPYESoppAY8UDbrkXKFz0e2FZASs']
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, vidtype='Movie', lang='en', sub_url=None, txt=''):
	
		urldata = client.b64encode(json.dumps('', encoding='utf-8'))
		params = client.b64encode(json.dumps('', encoding='utf-8'))
		
		online = check(url)
		files_ret = []
		titleinfo = ''
		fs = 0
		file_ext = '.mp4'
		try:
			furl, fs, file_ext = mega.get_mega_dl_link(url)
			if int(fs) == 0:
				fs = client.getFileSize(furl)
			urldata = createurldata(furl, quality)
		except Exception as e:
			online = False
			self.log('ERROR', 'createMeta', url, dolog=True)
			self.log('ERROR', 'createMeta', e, dolog=True)
		
		try:
			files_ret.append({'source':self.name, 'maininfo':'', 'titleinfo':titleinfo, 'quality':quality, 'vidtype':vidtype, 'rip':riptype, 'provider':provider, 'url':url, 'urldata':urldata, 'params':params, 'logo':logo, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'online':online, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':self.netloc[0], 'misc':{'player':'iplayer', 'gp':False}})
		except Exception as e:
			print "ERROR host_mega.py > createMeta : %s" % e.args
			files_ret.append({'source':urlhost, 'maininfo':'', 'titleinfo':titleinfo, 'quality':quality, 'vidtype':vidtype, 'rip':'Unknown' ,'provider':provider, 'url':url, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':self.netloc[0], 'misc':{'player':'iplayer', 'gp':False}})
			
		for fr in files_ret:
			links.append(fr)

		return links
		
	def resolve(self, url):
		return resolve(url)
			
	def resolveHostname(self, host):
		return self.name
		
	def testLink(self, url):
		return check(url)
	
def resolve(url):

	if check(url) == False: return
	
	return url

	
def check(url, headers=None, cookie=None):
	try:
		# http_res, red_url = client.request(url=url, output='responsecodeext', followredirect=True, headers=headers, cookie=cookie, httpsskip=True)
		# if str(http_res) not in client.HTTP_GOOD_RESP_CODES:
			# return False
			
		http_res = mega.send_http_request(url)
		#print http_res
		#print http_res.status
		if str(http_res.status) not in client.HTTP_GOOD_RESP_CODES:
			return False

		return True
	except:
		return False
		
def createurldata(mfile, qual):
	ret = ''
	
	try:
		#mfile = urllib.quote(mfile)
		mfile = unicode(mfile)
		qual = unicode(qual)
		files = []
		jsondata = {'label': qual, 'type': 'video/mp4', 'src': mfile, 'file': mfile, 'res': qual}
		jsondata = json.loads(json.dumps(jsondata))
		
		#print jsondata
		
		files.append(jsondata)
		
		if len(files) > 0:
			ret = files
	except Exception as e:
		print "Error in createurldata"
		print "URL : %s | Qual: %s" % (mfile, qual)
		print "Error: %s" % e
		
	#print ret
	ret = json.dumps(ret, encoding='utf-8')
	#print "urldata ------ %s" % ret
	return client.b64encode(ret)
		
def test(url):
	return resolve(url)

def log(type, name, msg):
	control.log('%s: %s %s' % (type, name, msg))
	
def logger(msg):
	control.log(msg)
