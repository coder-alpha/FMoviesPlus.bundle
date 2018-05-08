# -*- coding: utf-8 -*-

#########################################################################################################
#
# Streamango scrapper
#
# Adapted from tvaddonsco
# https://github.com/tvaddonsco/script.module.urlresolver/blob/master/lib/urlresolver/plugins/streamango.py
# and modified for use with Plex Media Server
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

name = 'streamango'
loggertxt = []
	
class host:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Apr. 11, 2018'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.logo = 'https://i.imgur.com/9Zv3dU8.png'
		self.name = name
		self.host = ['streamango.com', 'streamcherry.com', 'fruitstreams.com']
		self.netloc = ['streamango.com', 'streamcherry.com', 'fruitstreams.com']
		self.quality = '720p'
		self.loggertxt = []
		self.captcha = False
		self.allowsDownload = True
		self.resumeDownload = True
		self.allowsStreaming = True
		self.ac = False
		self.pluginManagedPlayback = True
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
		return ['https://streamango.com/embed/fnnnmermndekbbrf/']
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, vidtype='Movie', lang='en', sub_url=None, txt='', file_ext = '.mp4', testing=False, poster=None):
	
		if testing == True:
			links.append(url)
			return links
			
		if control.setting('Host-%s' % name) == False:
			log('INFO','createMeta','Host Disabled by User')
			return links
			
		orig_url = url
			
		urldata = client.b64encode(json.dumps('', encoding='utf-8'))
		params = client.b64encode(json.dumps('', encoding='utf-8'))
		
		online = check(url)
		vidurls, err, sub_url_t = getAllQuals(url, online)
		
		if vidurls == None:
			log(type='ERROR',method='createMeta-1', err=u'%s' % err)
			return links
			
		if sub_url_t != None:
			sub_url = sub_url_t
			
		files_ret = []
		
		for vv in vidurls:
			durl = vv['page']
			vidurl, r1, r2 = resolve(durl, online)
			if vidurl != None:
				quality = vv['label']
				try:
					#vidurl_t = client.request(vidurl, output='geturl')
					fs = client.getFileSize(vidurl)
					fs = int(fs)
				except Exception as e:
					log(type='ERROR',method='createMeta', err=u'%s' % e)
					fs = 0

				try:
					log(type='INFO',method='createMeta', err=u'durl:%s ; res:%s; fs:%s' % (vidurl,quality,fs))
					files_ret.append({'source':self.name, 'maininfo':'', 'titleinfo':txt, 'quality':quality, 'vidtype':vidtype, 'rip':riptype, 'provider':provider, 'url':durl, 'durl':durl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':fs, 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'poster':poster, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'misc':{'player':'iplayer', 'gp':False}})
				except Exception as e:
					log(type='ERROR',method='createMeta', err=u'%s' % e)
					files_ret.append({'source':urlhost, 'maininfo':'', 'titleinfo':txt, 'quality':quality, 'vidtype':vidtype, 'rip':'Unknown' ,'provider':provider, 'url':durl, 'durl':durl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':fs, 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'poster':poster, 'subdomain':client.geturlhost(url), 'misc':{'player':'iplayer', 'gp':False}})
			
		for fr in files_ret:
			links.append(fr)

		log('INFO', 'createMeta', 'Successfully processed %s link >>> %s' % (provider, orig_url), dolog=self.init)
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

		video_url = None
		err = ''
		try:
			page_link = url
			page_data_string = client.request(page_link, httpsskip=True)
			video_url = decode(page_data_string)
			if video_url[len(video_url)-1] == '@':
				video_url = video_url[:-1]
		except Exception as e:
			err = r
			log('ERROR', 'resolve', 'link > %s : %s' % (url, e), dolog=self.init)

		return (video_url, err, None)
		
	except Exception as e:
		e = '{}'.format(e)
		return (None, e, None)
		
def decode(html):
	
	source = None
	
	try:
		encoded = re.search('''srces\.push\({type:"video/mp4",src:\w+\('([^']+)',(\d+)''', html)
		if encoded:
			source = decode2(encoded.group(1), int(encoded.group(2)))
	except Exception as e:
		log('ERROR', 'decode', '%s' % (e), dolog=True)
	
	return source
		
def decode2(encoded, code):
		
	vid_url = ""
	k = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
	k = k[::-1]

	count = 0

	for index in range(0, len(encoded) - 1):
		while count <= len(encoded) - 1:
			dec1 = k.index(encoded[count])
			count += 1
			dec2 = k.index(encoded[count])
			count += 1
			dec3 = k.index(encoded[count])
			count += 1
			dec4 = k.index(encoded[count])
			count += 1

			t1 = ((dec1 << 2) | (dec2 >> 4))
			t2 = (((dec2 & 15) << 4) | (dec3 >> 2))
			t3 = ((dec3 & 3) << 6) | dec4
			t1 = t1 ^ code

			vid_url = str(vid_url) + chr(t1)

			if dec3 != 64:
				vid_url = str(vid_url) + chr(t2)
			if dec3 != 64:
				vid_url = str(vid_url) + chr(t3)

	if 'http' not in vid_url:
		vid_url = 'https:' + vid_url
	return vid_url

def getAllQuals(url, online=None):
	try:
		if online == None:
			if check(url) == False: 
				raise Exception('Video not available')
			
		page_data_string = client.request(url, httpsskip=True)
		video_url = decode(page_data_string)
		v_qs = video_url.split('/')
		v_qs = v_qs[len(v_qs)-1]
		v_qs = re.sub(r'[^0-9]', "", v_qs)
		v_qs = int(v_qs)
		video_url_a = []
		myheaders = {}
		myheaders['User-Agent'] = 'Mozilla'
		myheaders['Referer'] = url
		
		quals = [1080,720,480,360,256,128,64]
		for qs in quals:
			try:
				if v_qs == qs:
					f_i = {'label': '%sp' % qs, 'page':url}
					video_url_a.append(f_i)
					break
				elif v_qs > qs:
					i = quals.index(qs)
					f_i = {'label': '%sp' % quals[i-1], 'page':url}
					video_url_a.append(f_i)
					break
			except:
				pass
		
		video_urlf = video_url_a
		return (video_urlf, '', None)
	except Exception as e:
		e = '{}'.format(e)
		return (None, e, None)
	
def check(url, headers=None, cookie=None):
	try:
		http_res, red_url = client.request(url=url, output='responsecodeext', followredirect=True, headers=headers, cookie=cookie)
		if http_res not in client.HTTP_GOOD_RESP_CODES:
			return False
			
		page_data_string = client.request(url=url, headers=headers, cookie=cookie)
		if 'We are unable to find the video you\'re looking for' in page_data_string or 'Sorry!' in page_data_string or 'The file you are looking is currently converting' in page_data_string:
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
