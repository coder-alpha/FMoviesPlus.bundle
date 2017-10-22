# -*- coding: utf-8 -*-

#########################################################################################################
#
# Google scrapper
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

import re,urllib,json,time
import os, sys, ast

try:
	from resources.lib.libraries import client
	from resources.lib.libraries import control
except:
	pass


hdr = {
	'User-Agent': client.USER_AGENT,
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}

name = 'youtube'
	
class host:
	def __init__(self):
		self.logo = 'http://i.imgur.com/qZUP77r.png'
		self.name = name
		self.host = ['youtube.com']
		self.netloc = ['youtube.com']
		self.quality = '1080p'
		self.loggertxt = []
		self.captcha = False
		self.allowsDownload = False
		self.resumeDownload = False
		self.allowsStreaming = True
		self.ac = False
		self.pluginManagedPlayback = False
		self.speedtest = 0
		self.working = self.test()[0]
		self.resolver = self.test2()
		self.msg = ''

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
		return ['https://www.youtube.com/watch?v=HcRvwVwD1Sc']
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, vidtype='Movie', lang='en', sub_url=None, txt=''):
	
		urldata = client.b64encode(json.dumps('', encoding='utf-8'))
		params = client.b64encode(json.dumps('', encoding='utf-8'))
		
		online = check(url)
		files_ret = []
		fs = 5*1024*1024*1024
		
		try:
			files_ret.append({'source':self.name, 'maininfo':'', 'titleinfo':'', 'quality':quality, 'vidtype':vidtype, 'rip':riptype, 'provider':provider, 'url':url, 'durl':url, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':fs, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':self.netloc[0], 'misc':{'player':'eplayer', 'gp':False}})
		except Exception as e:
			print "ERROR host_youtube.py > createMeta : %s" % e.args
			files_ret.append({'source':urlhost, 'maininfo':'', 'titleinfo':'', 'quality':quality, 'vidtype':vidtype, 'rip':'Unknown' ,'provider':provider, 'url':url, 'durl':url, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':fs, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':self.netloc[0], 'misc':{'player':'eplayer', 'gp':False}})
			
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
		http_res, red_url = client.request(url=url, output='responsecodeext', followredirect=True, headers=headers, cookie=cookie)
		if http_res not in client.HTTP_GOOD_RESP_CODES:
			return False

		return True
	except:
		return False
		
def test(url):
	return resolve(url)
	
def log(type, name, msg):
	control.log('%s: %s %s' % (type, name, msg))
	
def logger(msg):
	control.log(msg)
