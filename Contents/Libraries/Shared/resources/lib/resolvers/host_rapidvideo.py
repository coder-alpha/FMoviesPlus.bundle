# -*- coding: utf-8 -*-

#########################################################################################################
#
# RapidVideo scrapper
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

name = 'rapidvideo'
loggertxt = []
	
class host:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.2'
		self.update_date = 'Dec. 28, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.logo = 'https://i.imgur.com/AG9ooWt.png'
		self.name = name
		self.host = ['rapidvideo.com']
		self.netloc = ['rapidvideo.com']
		self.quality = '1080p'
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
		return ['https://www.rapidvideo.com/v/FML5SEW27U']
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, vidtype='Movie', lang='en', sub_url=None, txt='', file_ext = '.mp4', testing=False):
	
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
					fs = client.getFileSize(vidurl)
					fs = int(fs)
				except:
					fs = 0

				try:
					log(type='INFO',method='createMeta', err=u'durl:%s ; res:%s; fs:%s' % (vidurl,quality,fs))
					files_ret.append({'source':self.name, 'maininfo':'', 'titleinfo':txt, 'quality':quality, 'vidtype':vidtype, 'rip':riptype, 'provider':provider, 'url':durl, 'durl':durl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':fs, 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'misc':{'player':'iplayer', 'gp':False}})
				except Exception as e:
					log(type='ERROR',method='createMeta', err=u'%s' % e)
					files_ret.append({'source':urlhost, 'maininfo':'', 'titleinfo':txt, 'quality':quality, 'vidtype':vidtype, 'rip':'Unknown' ,'provider':provider, 'url':durl, 'durl':durl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':fs, 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'misc':{'player':'iplayer', 'gp':False}})
			
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
			video_url = client.parseDOM(page_data_string, 'div', attrs = {'id': 'home_video'})[0]
			video_url = client.parseDOM(video_url, 'source', ret='src')[0]
		except Exception as e:
			err = r
			log('ERROR', 'resolve', 'link > %s : %s' % (url, e), dolog=self.init)

		return (video_url, err, None)
		
	except Exception as e:
		e = '{}'.format(e)
		return (None, e, None)

def getAllQuals(url, online=None):
	try:
		if online == None:
			if check(url) == False: 
				raise Exception('Video not available')
			
		video_url_a = []
		myheaders = {}
		myheaders['User-Agent'] = 'Mozilla'
		myheaders['Referer'] = url
		
		quals = ['1080p','720p','480p','360p']
		for qs in quals:
			try:
				page_link = (url + '&q=%s') % qs
				f_i = {'label':qs, 'page':page_link}
				video_url_a.append(f_i)
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
