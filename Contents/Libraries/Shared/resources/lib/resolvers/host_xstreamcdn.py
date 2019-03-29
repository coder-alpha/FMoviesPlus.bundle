# -*- coding: utf-8 -*-

#########################################################################################################
#
# Mp4upload scraper
#
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
from resources.lib.libraries import client, control, jsunpack

hdr = {
	'User-Agent': client.USER_AGENT,
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}

name = 'xstreamcdn'
loggertxt = []
	
class host:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Mar. 19, 2019'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.logo = 'https://i.imgur.com/b89saq1.png'
		self.name = name
		self.host = ['xstreamcdn.com']
		self.netloc = ['xstreamcdn.com']
		self.quality = '720p'
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
				bool = check(testUrl['url'])
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
				links = self.createMeta(testUrl['url'], 'Test', '', '720p', links, 'testing', 'BRRIP', page_url=testUrl['page_url'])
				if len(links) > 0:
					bool = True
					break
		except Exception as e:
			log(type='ERROR', method='testResolver', err=e)
			
		log(method='testResolver', err='%s parser status: %s' % (self.name, bool))
		return bool
		
	def testUrl(self):
		return [{'url':'https://www.xstreamcdn.com/v/3qo1y3pj2oy','page_url':'https://www1.gowatchseries.co/triple-frontier-episode-0'}]
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, vidtype='Movie', lang='en', sub_url=None, txt='', file_ext = '.mp4', testing=False, poster=None, headers=None, page_url=None):
	
		files_ret = []
		orig_url = url

		if testing == True:
			links.append(url)
			return links
			
		if control.setting('Host-%s' % name) == False:
			log('INFO','createMeta','Host Disabled by User')
			return links
			
		if '#' in url:
			url = url.split('#')[0]
			
		try:
			online = check(url)
			vidurls, err, sub_url_t = getAllQuals(url, page_url, online)
			
			if vidurls == None:
				log(type='ERROR',method='createMeta-1', err=u'%s' % err)
				return links
				
			if sub_url_t != None:
				sub_url = sub_url_t
			
			seq = 0
			for vv in vidurls: #{'quality':q, 'src':u, 'fs':fs, 'online':online, 'params':params, 'urldata':urldata}
				durl = url
				vidurl = vv['src']
				
				if vidurl != None:
					quality = vv['quality']
					fs = int(vv['fs'])
					online = vv['online']
					params = vv['params']
					urldata = vv['urldata']
					
					try:
						log(type='INFO',method='createMeta', err=u'durl:%s ; res:%s; fs:%s' % (durl,quality,fs))
						files_ret.append({'source':self.name, 'maininfo':'', 'titleinfo':txt, 'quality':quality, 'vidtype':vidtype, 'rip':riptype, 'provider':provider, 'orig_url':orig_url, 'url':vidurl, 'durl':durl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'poster':poster, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'page_url':page_url, 'misc':{'player':'iplayer', 'gp':True}, 'seq':seq})
					except Exception as e:
						log(type='ERROR',method='createMeta', err=u'%s' % e)
						files_ret.append({'source':urlhost, 'maininfo':'', 'titleinfo':txt, 'quality':quality, 'vidtype':vidtype, 'rip':'Unknown' ,'provider':provider, 'orig_url':orig_url, 'url':vidurl, 'durl':durl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'poster':poster, 'subdomain':client.geturlhost(url), 'page_url':page_url, 'misc':{'player':'iplayer', 'gp':True}, 'seq':0})
					seq += 1
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
		
	def resolve(self, url, page_url=None, online=None, **kwargs):
		return resolve(url, page_url=page_url, online=online)
			
	def resolveHostname(self, host):
		return self.name
		
	def testLink(self, url):
		return check(url)
	
def resolve(url, page_url=None, online=None, **kwargs):

	try:
		if online == None:
			if check(url) == False: 
				raise Exception('Video not available')
		elif online == False:
			raise Exception('Video not available')

		video_url = None
		err = ''
		try:
			video_url, err = decode(url, page_url)
			if video_url == None or len(video_url) == 0:
				raise Exception(err)
		except Exception as e:
			err = e
			log('ERROR', 'resolve', 'link > %s : %s' % (url, e), dolog=True)

		return (video_url, err, None)
		
	except Exception as e:
		e = '{}'.format(e)
		return (None, e, None)
		
def decode(url,page_url):
	items = []
	err = ''
	try:
		id = re.compile('//.+?/(?:embed|v)/([0-9a-zA-Z-_]+)').findall(url)[0]
		headersx = {'Referer': url, 'User-Agent': client.agent()}
		post_data = {'r':page_url, 'd':'www.xstreamcdn.com'}
		api_url = 'https://www.xstreamcdn.com/api/source/%s' % id
		page_data = client.request(api_url, post=client.encodePostData(post_data), headers=headersx)
		
		j_data = json.loads(page_data)
		success = j_data['success']
		if success == False:
			raise Exception('API returned error: %s | Data: %s' % (api_url, post_data))
		else:
			srcs = j_data['data']
			for src in srcs:
				q = src['label']
				u = src['file']
				fs = client.getFileSize(u, retry429=True, headers=headersx)
				online = check(u)
				u1 = client.request(u, output='geturl')
				if u1 != None:
					u = u1
				urldata = client.b64encode(json.dumps('', encoding='utf-8'))
				params = client.b64encode(json.dumps('', encoding='utf-8'))
				paramsx = {'headers':headersx}
				params = client.b64encode(json.dumps(paramsx, encoding='utf-8'))
				
				items.append({'quality':q, 'src':u, 'fs':fs, 'online':online, 'params':params, 'urldata':urldata})
		if len(items) == 0:
			raise Exception('No videos found !')
	except Exception as e:
		err = 'xtreamcdn Error: %s' % e
			
	return items, err

def getAllQuals(url, page_url, online=None):
	try:
		if online == None:
			if check(url) == False: 
				raise Exception('Video not available')
			
		video_urls, err = decode(url, page_url)
		
		if video_urls == None or len(video_urls) == 0 or err != '':
			raise Exception(err)
		
		video_urlf = video_urls
		return (video_urlf, '', None)
	except Exception as e:
		e = '{}'.format(e)
		return (None, e, None)
		
def qual_based_on_fs(fs):
	q = '480p'
	try:
		if int(fs) > 2 * float(1024*1024*1024):
			q = '1080p'
		elif int(fs) > 1 * float(1024*1024*1024):
			q = '720p'
	except:
		pass
	return q
	
def check(url, headers=None, cookie=None):
	try:
		http_res, red_url = client.request(url=url, output='responsecodeext', followredirect=True, headers=headers, cookie=cookie)
		if http_res not in client.HTTP_GOOD_RESP_CODES:
			return False
			
		page_data_string = client.request(url=url, headers=headers, cookie=cookie)
		
		if 'File Not Found' in page_data_string or 'File was deleted' in page_data_string:
			return False
	
		return True
	except:
		return False
		
def test(url, page_url=None):
	return resolve(url, page_url)
	
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
