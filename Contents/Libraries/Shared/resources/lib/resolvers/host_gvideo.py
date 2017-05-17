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
from resources.lib.libraries import client
from resources.lib.libraries import control

hdr = {
	'User-Agent': client.USER_AGENT,
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}
	
FORMATS_EXT = {
        '5': 'flv',
        '6': 'flv',
        '13': '3gp',
        '17': '3gp',
        '18': 'mp4',
        '22': 'mp4',
        '34': 'flv',
        '35': 'flv',
        '36': '3gp',
        '37': 'mp4',
        '38': 'mp4',
        '43': 'webm',
        '44': 'webm',
        '45': 'webm',
        '46': 'webm',
        '59': 'mp4'
    }
	
CONTAINER_KEYS = ['flv','mp4','3gp','webm','mkv','ftypisom','matroska']

name = 'gvideo'
	
class host:
	def __init__(self):
		self.logo = 'http://i.imgur.com/KYtgDP6.png'
		self.name = 'gvideo'
		self.host = ['google.com','blogspot.com','googlevideo.com','googleusercontent.com']
		self.netloc = ['google.com','blogspot.com','googlevideo.com','googleusercontent.com']
		self.quality = '1080p'
		self.captcha = False
		self.ac = False
		self.pluginManagedPlayback = True
		self.speedtest = 0
		self.testResult = self.test()[0]
		self.msg = ''
		self.useGetLinkAPI = False
		self.checkGetLinkAPI()
		self.UA = client.USER_AGENT

	def info(self):
		return {
			'name': self.name,
			'class': self.name,
			'speed': round(self.speedtest,3),
			'netloc': self.netloc,
			'host': self.host,
			'quality': self.quality,
			'logo': self.logo,
			'working': self.testResult,
			'captcha': self.captcha,
			'msg': self.msg,
			'playbacksupport': self.pluginManagedPlayback,
			'a/c': self.ac
		}
		
	def checkGetLinkAPI(self):
		print "entering checkGetLinkAPI"
		http_res, content = client.request(url='http://api.getlinkdrive.com', output='response', use_web_proxy=False)
		print 'http://api.getlinkdrive.com Response: %s' % http_res
		if http_res in client.HTTP_GOOD_RESP_CODES:
			self.useGetLinkAPI = True
		else:
			self.useGetLinkAPI = False
		
	def test(self):
		try:
			testUrls = self.testUrl()
			bool = False
			msg = []
			for testUrl in testUrls:
				x1 = time.time()
				bool = check(testUrl)[0]
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
				links = self.createMeta(testUrl, 'Test', '', '', links, 'testing')
				print links
		except Exception as e:
			print "Error: %s" % e
		
	def testUrl(self):
		return ['https://drive.google.com/file/d/0B6VYU2mjTdy0WVRjb1BJUU1hYXM/view']
		
	def createMeta(self, url, provider, logo, quality, links, key, showsplit=True, useGetlinkAPI=True, vidtype='Movie'):
	
		if 'http' not in url and 'google.com/file' in url:
			url = 'https://drive.google.com/' + url.split('.com/')[1]
				
		#print "createMeta1 : %s %s %s %s" % (url, provider, logo, quality)
		videoData, headers, content, cookie = getVideoMetaData(url)
		try:
			cookie += '; %s' % content['Set-Cookie']
		except:
			pass
		#print cookie
		
		#cookie_value = cookie
		#cookie_value = client.search_regex(r"DRIVE_STREAM=([^;]+);", cookie, 'cookie val',group=1)
		#domain = client.search_regex(r"https?://([^\/]+)", url, 'host val', group=1)
		#cookie = 'DRIVE_STREAM=%s' % (cookie_value)
		
		#cookie = urllib.quote_plus(cookie).replace('+','%20').replace('%2F','/')
		# DRIVE_STREAM%3Dva1wsBbVn3A%3B%20path%3D/%3B%20domain%3D.docs.google.com%3B
		# DRIVE_STREAM%3DtV76KFL8a6k%3B+path%3D%2F%3B+domain%3D.docs.google.com%3B
		
		params = {'headers':headers,'cookie':cookie}
		params = json.dumps(params, encoding='utf-8')
		params = client.b64encode(params)
		
		quality = file_quality(url, quality, videoData)[0]
		isOnline = check(url, videoData, headers=headers, cookie=cookie)[0]
		type = rip_type(url, quality)
		
		files = []
		
		#print "createMeta : %s %s %s %s" % (url, provider, logo, quality)
		titleinfo = ''
		files_ret = []

		enabled = True
		try:
			#udata = urldata(url, videoData=videoData, usevideoData=True)			
			if 'google.com/file' in url:
				enabled = False
			files_ret.append({'source':self.name, 'maininfo':'', 'titleinfo':titleinfo, 'quality':quality, 'vidtype':vidtype, 'rip':type, 'provider':provider, 'url':url, 'urldata':urldata('',''), 'params':params, 'logo':logo, 'online':isOnline, 'key':key, 'enabled':enabled, 'ts':time.time()})
		except Exception as e:
			print '%s > createMeta-1 ERROR: %s for URL: %s' % (self.name, e, url)
			
		isGetlinkWork = False
		try:
			if useGetlinkAPI==True and isOnline and 'google.com/file' in url and self.useGetLinkAPI:
				client.setIP4()
				titleinfo = ' | (via GetLink API) '
				files = urldata(url)
				files = client.b64decode(files)
				filesJ = json.loads(files)
				if len(filesJ) > 0:
					for mfile in filesJ:
						mfile = json.loads(mfile)
						#print "mfile --- : %s" % mfile
						furl = mfile['src']
						f2url = client.request(furl, followredirect=True, output='geturl')
						if 'http' in f2url:
							furl = f2url
							#print "furl --- : %s" % furl
							quality = file_quality(furl, mfile['res'], videoData)[0]
							isOnlineT = check(furl, videoData, headers=headers, cookie=cookie)[0]
							type = rip_type(furl, quality)
						else:
							isOnlineT = 'Unknown'
						
						p = {'headers':'','cookie':''}
						p = json.dumps(p, encoding='utf-8')
						p = client.b64encode(p)
						
						files_ret.append({'source': self.name, 'maininfo':'', 'titleinfo':titleinfo, 'quality': quality, 'vidtype':vidtype, 'rip':type, 'provider': provider, 'url': furl, 'urldata':urldata('',''), 'params':p, 'logo': logo, 'online': isOnlineT, 'key':key, 'enabled':True, 'ts':time.time()})
						isGetlinkWork = True
				client.setIP6()
		except Exception as e:
			client.setIP6()
			print '%s > createMeta-2 ERROR: %s for URL: %s' % (self.name, e, url)
			
		try:
			if showsplit == True and isOnline and isGetlinkWork == False:
				# currently suffers from transcoding failure on most clients
				files = get_files(url, videoData)[0]
				for furl in files:
					quality = file_quality(furl, quality, videoData)[0]
					type = rip_type(furl, quality)
					
					furl = urllib.unquote(furl).decode('utf8')
					furl = furl.decode('unicode_escape')
					
					isOnlineT = check(furl, videoData, headers=headers, cookie=cookie)[0]
					
					files_ret.append({'source': self.name, 'maininfo':'', 'titleinfo':'', 'quality': quality, 'vidtype':vidtype, 'rip':type, 'provider': provider, 'url': furl, 'urldata':urldata('',''), 'params':params, 'logo': logo, 'online': isOnlineT, 'key':key, 'enabled':enabled, 'ts':time.time()})
		except Exception as e:
			print '%s > createMeta-3 ERROR: %s for URL: %s' % (self.name, e, url)

			
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

	if check(url)[0] == False: return
	
	return url

def getVideoMetaData(url):
	try:
		res = ('', '', '', '')
		
		if 'google.com/file' in url:
			r_split = url.split('/')
			meta_url = 'https://docs.google.com/get_video_info?docid=%s' % r_split[len(r_split)-2]
			#print meta_url
			
			headers = {}
			headers['User-Agent'] = client.USER_AGENT
			result, headers, content, cookie = client.request(meta_url, output = 'extended', headers=headers, IPv4=True)
			#print content
			return (result, headers, content, cookie)
		return res
	except Exception as e:
		print 'ERROR: %s' % e
		return res
	
def check(url, videoData=None, headers=None, cookie=None, doPrint=False):
	try:
		if 'google.com/file' in url:
			if videoData==None:
				videoData = getVideoMetaData(url)[0]
			
			if 'This+video+doesn%27t+exist' in videoData:  
				log('Check Fail', name, 'This video doesn\'t exist : %s' % url)
				return (False, videoData)
			
			res_split = videoData.split('&')
			for res in res_split:
				if 'status' in res:
					if 'fail' in res:
						log('Check Fail', name, 'status == fail')
						return (False, videoData)
		else:
			http_res, red_url = client.request(url=url, output='responsecodeext', followredirect=True, headers=headers, cookie=cookie, IPv4=True)
			key_found = False
			if http_res in client.HTTP_GOOD_RESP_CODES:
				chunk = client.request(url=red_url, output='chunk', headers=headers, cookie=cookie, IPv4=True) # dont use web-proxy when retrieving chunk
				if doPrint:
					print "url --- %s" % red_url
					print "chunk --- %s" % chunk[0:20]
				
				for key in CONTAINER_KEYS:
					if key.lower() in str(chunk[0:20]).lower():
						key_found = True
						break
			else:
				log('Check Fail', name, 'HTTP Resp:%s for url: %s' % (http_res, url))
				return (False, videoData)
			if key_found == False:
				log('Check Fail', name, 'keyword in chunk not found : %s --- Chunk: %s' % (url,chunk[0:20]))
				return (False, videoData)

		return (True, videoData)
	except:
		return (False, videoData)

def urldata(url, videoData=None, usevideoData=False):
	ret = ''
	#print "urldata ----------- %s" % url
	try:
		if usevideoData==True and videoData != None and videoData != '':
			#print "urldata using videoData"
			files = []
			res_split = videoData.split('&')
			for res in res_split:
				if 'fmt_stream_map' in res:
					file_data = res.split('=')[1]
					file_data = urllib.unquote(file_data).decode('utf8')
					files_split = file_data.split(',')
					for file in files_split:
						mfile = file.split('|')[1]
						qual = file_quality(mfile, '360p')[0]
						jsondata = {
							"label": qual,
							"type": "video/mp4",
							"src": mfile,
							"file": mfile,
							"res": qual
						}
						files.append(jsondata)
						#print mfile
					break
			if len(files) > 0:
				ret = files
		elif 'google.com/file' in url:
			#print "urldata using getlink API"
			r_split = url.split('/')
			getlinkurl = 'http://api.getlinkdrive.com/getlink?url=https://drive.google.com/file/d/%s/view' % r_split[len(r_split)-2]
			print "Getlink-API URL: %s" % getlinkurl
			c = 0
			files = []
			while ret == '' or len(files) == 0 and c < 3:
				ret = client.request(getlinkurl, IPv4=True)
				ret = ret.split('},{')
				for r in ret:
					r = r.replace('{','').replace('}','').replace('[','').replace(']','')
					files.append('{%s}' % r)
				c += 1
			if len(files) > 0:
				ret = files
	except:
		print "Error in urldata"
		pass
		
	#print ret
	ret = json.dumps(ret, encoding='utf-8')
	#print "urldata ------ %s" % ret
	return client.b64encode(ret)
	
def rip_type(url, type):
	try:
		i =  int(type.replace('p','')) # fail when type = TS, CAM, etc.
		type = 'brrip'
	except:
		pass
	try:
		url = url.lower()
		if '.brrip.' in url:
			type = 'brrip'
		elif '.ts.' in url:
			type = 'ts'
		elif '.cam.' in url:
			type = 'cam'
		elif '.scr.' in url:
			type = 'scr'
			
		type = type.lower()
		if type == 'brrip' or type == 'ts' or type == 'cam' or type == 'scr':
			pass
		else:
			type = 'unknown'
		
		return unicode(type.upper())
	except:
		return unicode('Unknown'.upper())
		
def get_files(url, videoData=None):

	try:
		files = []
		if 'google.com/file' in url:
			if videoData==None:
				videoData = getVideoMetaData(url)[0]
			res_split = videoData.split('&')
			for res in res_split:
				if 'fmt_stream_map' in res:
					file_data = res.split('=')[1]
					file_data = urllib.unquote(file_data).decode('utf8')
					files_split = file_data.split(',')
					for file in files_split:
						mfile = file.split('|')[1]
						files.append(mfile)
						#print mfile
					break
		
		return (files, videoData)
	except:
		return (files, videoData)
	
def file_quality(url, quality, videoData=None):

	try:
		if 'google.com/file' in url:
			if videoData==None:
				videoData = getVideoMetaData(url)[0]
			res_split = videoData.split('&')
			for res in res_split:
				if 'fmt_list' in res:
					if 'x1080' in res:
						quality = '1080p'
					elif 'x720' in res:
						quality = '720p'
					elif 'x480' in res:
						quality = '480p'
					else:
						quality = '360p'
		else:
			qual = re.compile('itag=(\d*)').findall(url)
			qual += re.compile('=m(\d*)$').findall(url)
			try: qual = qual[0]
			except: return (unicode(quality), videoData)

			if qual in ['37', '137', '299', '96', '248', '303', '46']:
				quality = u'1080p'
			elif qual in ['22', '84', '136', '298', '120', '95', '247', '302', '45', '102']:
				quality = u'720p'
			elif qual in ['35', '44', '135', '244', '94', '59']:
				quality = u'480p'
			elif qual in ['18', '34', '43', '82', '100', '101', '134', '243', '93']:
				quality = u'360p'
			elif qual in ['5', '6', '36', '83', '133', '242', '92', '132']:
				quality = u'360p'
		
		return (unicode(quality), videoData)
	except:
		return (unicode(quality), videoData)
		
def test(url):
	return resolve(url)
	
def log(type, name, msg):
	control.log('%s: %s %s' % (type, name, msg))
