# -*- coding: utf-8 -*-

#########################################################################################################
#
# Vidcloud scraper
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
from __builtin__ import eval

try:
	from resources.lib.libraries import client
	from resources.lib.libraries import control
	from resources.lib import resolvers
except:
	pass

hdr = {
	'User-Agent': client.USER_AGENT,
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}

name = 'vidcloud'
loggertxt = []
	
class host:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.2'
		self.update_date = 'Feb. 12, 2019'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.logo = 'https://i.imgur.com/Phbe6Z3.png'
		self.name = name
		self.host = ['vidcloud.icu']
		self.netloc = ['vidcloud.icu']
		self.quality = '1080p'
		self.loggertxt = []
		self.captcha = False
		self.allowsDownload = True
		self.resumeDownload = True
		self.allowsStreaming = True
		self.ac = False
		self.pluginManagedPlayback = False
		self.speedtest = 0
		testResults = self.testWorking()
		self.working = testResults[0]
		self.msg = testResults[1]
		if self.working == False:
			self.captcha = True
			self.working = True
		self.resolver = self.testResolver()
		self.init = True
		log(type='INFO', method='init', err=' -- Initializing %s %s %s End --' % (name, self.ver, self.update_date))

	def info(self):
		return {
			'name': self.name,
			'ver': self.ver,
			'date': self.update_date,
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
					
	def getLog(self):
		self.loggertxt = loggertxt
		return self.loggertxt
		
	def testWorking(self):
		try:
			testUrls = self.testUrl()
			bool = False
			msg = ''
			for testUrl in testUrls:
				x1 = time.time()
				bool = check(testUrl)
				self.speedtest = time.time() - x1
				
				if bool == True:
					break
				
			log(method='testWorking', err='%s online status: %s' % (self.name, bool))
			return (bool, msg)
		except Exception as e:
			log(method='testWorking', err='%s online status: %s' % (self.name, bool))
			log(type='ERROR', method='testWorking', err=e)
			return False, msg
			
	def testResolver(self):
		try:
			if control.setting('use_quick_init') == True:
				log('INFO','testResolver', 'Disabled testing - Using Quick Init setting in Prefs.')
				return False
			testUrls = self.testUrl()
			links = []
			bool = False
			for testUrl in testUrls:
				links = self.createMeta(testUrl, 'Test', '', '720p', links, 'testing', 'BRRIP')
				if len(links) > 0:
					bool = True
					break
		except Exception as e:
			log(type='ERROR', method='testResolver', err=e)
			
		log(method='testResolver', err='%s parser status: %s' % (self.name, bool))
		return bool
		
	def testUrl(self):
		return ['https://vidcloud.icu/streaming.php?id=MjMwOTg2&title=Bumblebee&typesub=SUB&sub=L2J1bWJsZWJlZS9idW1ibGViZWUudnR0&cover=Y292ZXIvYnVtYmxlYmVlLnBuZw==']
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, vidtype='Movie', lang='en', sub_url=None, txt='', file_ext = '.mp4', testing=False, poster=None, headers=None, page_url=None):
	
		files_ret = []
		orig_url = url
		
		if testing == True:
			links.append(url)
			return links
			
		if control.setting('Host-%s' % name) == False:
			log('INFO','createMeta','Host Disabled by User')
			return links
			
		try:
			if 'vidcloud.icu/load' in url:
				raise Exception('No mp4 Video\'s found')
			elif url != None:
				online = True
				result = client.request(orig_url, httpsskip=True)
				if 'Sorry, this video reuploading' in result:
					online = False
				
				if online == True:
					vids = client.parseDOM(result, 'ul', attrs = {'class': 'list-server-items'})[0]
					vids = client.parseDOM(vids, 'li', attrs = {'class': 'linkserver'}, ret='data-video')
					vids = list(set(vids))
					for video_url in vids:
						video_urlx = video_url
						if 'http' not in video_urlx:
							video_urlx = 'http:' + video_urlx
						if video_urlx != None and 'vidcloud.icu/load' not in video_urlx:
							video_url1 = '%s' % client.request(video_urlx, followredirect=True, httpsskip=True, output='geturl')
							if video_url1 != None and 'http' in video_url1 and 'vidcloud.icu' not in video_url1:
								try:
									files_ret = resolvers.createMeta(video_url1, provider, logo, quality, files_ret, key, poster=poster, riptype=riptype, vidtype=vidtype, sub_url=sub_url, testing=testing, headers=headers, page_url=page_url)
								except Exception as e:
									log(type='ERROR',method='createMeta', err=u'%s' % e)
						elif video_urlx != None and 'vidcloud.icu/load' in video_urlx:
							id = re.findall(r'id=(.*?)&',video_urlx)[0]
							u = 'https://vidcloud.icu/download?id=%s' % id
							res = client.request(u)
							mp4_vids = re.findall(r'http.*?mp4',res)
							if len(mp4_vids) > 0:
								try:
									files_ret = resolvers.createMeta(u, provider, logo, quality, files_ret, key, poster=poster, riptype=riptype, vidtype=vidtype, sub_url=sub_url, testing=testing, headers=headers, page_url=page_url, urlhost='vidcloud.icu/download')
								except Exception as e:
									log(type='ERROR',method='createMeta', err=u'%s' % e)
							elif len(mp4_vids) == 0 and video_url == vids[len(vids)-1] and len(files_ret) == 0:
								raise Exception('No mp4 Video\'s found')
		except Exception as e:
			log('ERROR', 'createMeta', '%s' % e)
		
		for fr in files_ret:
			links.append(fr)

		if len(files_ret) > 0:
			log('SUCCESS', 'createMeta', 'Successfully processed %s link >>> %s' % (provider, orig_url), dolog=self.init)
		else:
			log('FAIL', 'createMeta', 'Failed in processing %s link >>> %s' % (provider, orig_url), dolog=self.init)
			
		log('INFO', 'createMeta', 'Completed', dolog=self.init)
			
		return links
		
	def resolve(self, url):
		return resolve(url)
			
	def resolveHostname(self, host):
		return self.name
		
	def testLink(self, url):
		return check(url)
	
def resolve(url, online=None):

	try:
		if online == None:
			if check(url) == False: 
				raise Exception('Video not available')

		return (url, '', None)
		
	except Exception as e:
		e = '{}'.format(e)
		return (None, e, None)
	
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
	
def log(type='INFO', method='undefined', err='', dolog=True, logToControl=False, doPrint=True):
	try:
		msg = '%s: %s > %s > %s : %s' % (time.ctime(time.time()), type, name, method, err)
		if dolog == True:
			loggertxt.append(msg)
		if logToControl == True:
			control.log(msg)
		if control.doPrint == True and doPrint == True:
			print msg
	except Exception as e:
		control.log('Error in Logging: %s >>> %s' % (msg,e))
