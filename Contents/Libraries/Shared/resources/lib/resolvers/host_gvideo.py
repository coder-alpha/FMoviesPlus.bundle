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
	
CONTAINER_KEYS = ['flv','mp4','3gp','webm','mkv','ftypisom','matroska','ftypmp42', 'isommp42', 'lmvhd']

FMOVIES_SERVER_MAP = {'Server F1':' Google-F1 (blogspot.com)','Server F2':' Google-F2 (blogspot.com)','Server F3':' Google-F3 (blogspot.com)','Server F4':' Google-F4 (blogspot.com)', 'Server G1':'Google-G1 (googleapis.com)', 'Server G2':'Google-G2 (googleusercontent.com)', 'Server G3':'Google-G3 (googleusercontent.com)', 'Server G4':'Google-G4 (googleapis.com)'}

name = 'gvideo'
loggertxt = []
	
class host:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Nov. 13, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.logo = 'http://i.imgur.com/KYtgDP6.png'
		self.name = 'gvideo'
		self.host = ['google.com','blogspot.com','googlevideo.com','googleusercontent.com','googleapis.com']
		self.netloc = ['google.com','blogspot.com','googlevideo.com','googleusercontent.com','googleapis.com']
		self.quality = '1080p'
		self.loggertxt = []
		self.captcha = False
		self.useGetLinkAPI = False
		self.allowsDownload = True
		self.resumeDownload = True
		self.allowsStreaming = True
		self.ac = False
		self.pluginManagedPlayback = True
		self.speedtest = 0
		self.working = self.testWorking()[0]
		self.resolver = self.testResolver()
		self.msg = ''
		#self.checkGetLinkAPI()
		self.UA = client.USER_AGENT
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
		
	def checkGetLinkAPI(self):
		print "entering checkGetLinkAPI"
		http_res, content = client.request(url='http://api.getlinkdrive.com', output='response', use_web_proxy=False)
		print 'http://api.getlinkdrive.com Response: %s' % http_res
		if http_res in client.HTTP_GOOD_RESP_CODES or http_res in client.GOOGLE_HTTP_GOOD_RESP_CODES_1:
			self.useGetLinkAPI = True
		else:
			self.useGetLinkAPI = False
		
	def testWorking(self):
		try:
			testUrls = self.testUrl()
			bool = False
			msg = []
			for testUrl in testUrls:
				x1 = time.time()
				bool = check(testUrl)[0]
				self.speedtest = time.time() - x1
				msg.append([bool, testUrl])
				if bool == True:
					break
				
			log(method='testWorking', err='%s online status: %s' % (self.name, bool))
			return (bool,msg)
		except Exception as e:
			log(method='testWorking', err='%s online status: %s' % (self.name, bool))
			log(type='ERROR', method='testWorking', err=e)
			return False
			
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
		return ['https://drive.google.com/file/d/0B0JMGMGgxp9WMEdWb1hyQUhlOWs/view','https://drive.google.com/file/d/0B1XiKAQcEMeHc2ZIXzB4RDJ6Z1k/view']
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, showsplit=False, useGetlinkAPI=True, vidtype='Movie', lang='en', sub_url=None, txt='', file_ext = '.mp4', testing=False):
	
		orig_url = url
		
		if testing == True:
			links.append(url)
			return links
			
		if control.setting('Host-%s' % name) == False:
			log('INFO','createMeta','Host Disabled by User')
			return links
	
		if 'http' not in url and 'google.com/file' in url:
			url = 'https://drive.google.com/' + url.split('.com/')[1]
			
		httpsskip = False
		if control.setting('use_https_alt') != None and (control.setting('use_https_alt') == True or control.setting('use_https_alt') == False):
			httpsskip = control.setting('httpsskip')
				
		#print "createMeta1 : %s %s %s %s" % (url, provider, logo, quality)
		videoData, headers, content, cookie = getVideoMetaData(url, httpsskip)
		try:
			cookie += '; %s' % content['Set-Cookie']
			# cookie_s = cookie.split(';')
			# cookie_n = []
			# for cook in cookie_s:
				# cook = cook.strip()
				# if '=' in cook and cook not in cookie_n:
					# cookie_n.append(cook)
			# cookie = ('; '.join(x for x in sorted(cookie_n)))
			cookie_value = client.search_regex(r"DRIVE_STREAM=([^;]+);", cookie, 'cookie val',group=1)
			domain = client.search_regex(r"https?://([^\/]+)", url, 'host val', group=1)
			cookie = 'DRIVE_STREAM=%s; path=/; domain=.%s;' % (cookie_value, domain)
		except:
			pass
		#print cookie
		
		#cookie = urllib.quote_plus(cookie).replace('+','%20').replace('%2F','/')
		# DRIVE_STREAM%3Dva1wsBbVn3A%3B%20path%3D/%3B%20domain%3D.docs.google.com%3B
		# DRIVE_STREAM%3DtV76KFL8a6k%3B+path%3D%2F%3B+domain%3D.docs.google.com%3B
		
		params = {'headers':headers,'cookie':cookie}
		params = json.dumps(params, encoding='utf-8')
		params = client.b64encode(params)
		
		if client.geturlhost(url) in self.host[4]:
			pass # skip for googleapis.com link
		else:
			quality = file_quality(url, quality, videoData)[0]
		isOnline = check(url, videoData, headers=headers, cookie=cookie, httpsskip=httpsskip)[0]
		type = rip_type(url, riptype)
		
		files = []
		
		#print "createMeta : %s %s %s %s" % (url, provider, logo, quality)
		titleinfo = txt
		if txt != '':
			titleinfo = txt
		ntitleinfo = titleinfo
		
		files_ret = []
		
		enabled = True
		try:
			#udata = urldata(url, videoData=videoData, usevideoData=True)			
			if 'google.com/file' in url:
				idstr = '%s' % (url.split('/preview')[0].split('/edit')[0].split('/view')[0])
				idstr = idstr.split('/')
				id = idstr[len(idstr)-1]
				try:
					durl, f_res, fs = getFileLink(id, httpsskip)
				except:
					fs = 0
					durl = None
					
				if durl != None:
					files_ret.append({'source':self.name, 'maininfo':'', 'titleinfo':ntitleinfo, 'quality':quality, 'vidtype':vidtype, 'rip':type, 'provider':provider, 'url':durl, 'durl':durl, 'urldata':createurldata(durl,quality), 'params':params, 'logo':logo, 'online':isOnline, 'allowsDownload':self.allowsDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':enabled, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(durl), 'misc':{'player':'iplayer', 'gp':False}})
				else:
					fs = client.getFileSize(url, retry429=True)
					
				files_ret.append({'source':self.name, 'maininfo':'', 'titleinfo':ntitleinfo, 'quality':quality, 'vidtype':vidtype, 'rip':type, 'provider':provider, 'url':url, 'durl':url, 'urldata':urldata('',''), 'params':params, 'logo':logo, 'online':isOnline, 'allowsDownload':self.allowsDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':enabled, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'misc':{'player':'eplayer', 'gp':False}})
			else:
				fs = client.getFileSize(url, retry429=True)
				
				files_ret.append({'source':self.name, 'maininfo':'', 'titleinfo':ntitleinfo, 'quality':quality, 'vidtype':vidtype, 'rip':type, 'provider':provider, 'url':url, 'durl':url, 'urldata':urldata('',''), 'params':params, 'logo':logo, 'online':isOnline, 'allowsDownload':self.allowsDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':enabled, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'misc':{'player':'iplayer', 'gp':False}})
		except Exception as e:
			log(type='ERROR',method='createMeta-1', err=u'%s' % e)
			
		isGetlinkWork = False
		try:
			if useGetlinkAPI==True and isOnline and 'google.com/file' in url and self.useGetLinkAPI:
				client.setIP4()
				ntitleinfo = titleinfo + ' | (via GetLink API) '
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
							type = rip_type(furl, riptype)
						else:
							isOnlineT = 'Unknown'
						
						p = {'headers':'','cookie':''}
						p = json.dumps(p, encoding='utf-8')
						p = client.b64encode(p)
						
						fs = client.getFileSize(furl, retry429=True)
						
						files_ret.append({'source': self.name, 'maininfo':'', 'titleinfo':ntitleinfo, 'quality': quality, 'vidtype':vidtype, 'rip':type, 'provider': provider, 'url': furl, 'durl':furl, 'urldata':urldata('',''), 'params':p, 'logo': logo, 'online': isOnlineT, 'allowsDownload':self.allowsDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':enabled, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(furl), 'misc':{'player':'iplayer' , 'gp':False}})
						isGetlinkWork = True
				client.setIP6()
		except Exception as e:
			log(type='ERROR',method='createMeta-2', err=u'%s' % e)
			
		try:
			if showsplit == True and isOnline and isGetlinkWork == False:
				# currently suffers from transcoding failure on most clients
				ntitleinfo = titleinfo + ' | *limited support* '
				files = get_files(url, videoData)[0]
				for furl in files:
					quality = file_quality(furl, quality, videoData)[0]
					type = rip_type(furl, riptype)
					
					furl = urllib.unquote(furl).decode('utf8')
					furl = furl.decode('unicode_escape')
					
					isOnlineT = check(furl, videoData, headers=headers, cookie=cookie)[0]
					
					fs = client.getFileSize(furl, retry429=True)
					
					files_ret.append({'source': self.name, 'maininfo':'', 'titleinfo':ntitleinfo, 'quality': quality, 'vidtype':vidtype, 'rip':type, 'provider': provider, 'url': furl, 'durl':furl, 'urldata':createurldata(furl,quality), 'params':params, 'logo': logo, 'online': isOnlineT, 'allowsDownload':self.allowsDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':enabled, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(furl), 'misc':{'player':'iplayer', 'gp':False}})
		except Exception as e:
			log(type='ERROR',method='createMeta-3', err=u'%s' % e)

			
		for fr in files_ret:
			fr['resumeDownload'] = self.resumeDownload
			links.append(fr)
		
		log('INFO', 'createMeta', 'Successfully processed %s link >>> %s' % (provider, orig_url), dolog=self.init)
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

def getVideoMetaData(url, httpsskip=False):
	try:
		res = ('', '', '', '')
		
		if 'google.com/file' in url:
			r_split = url.split('/')
			meta_url = 'https://docs.google.com/get_video_info?docid=%s' % r_split[len(r_split)-2]
			#print meta_url
			
			headers = {}
			headers['User-Agent'] = client.USER_AGENT
			result, headers, content, cookie = client.request(meta_url, output = 'extended', headers=headers, IPv4=True, httpsskip=httpsskip)
			#print content
			return (result, headers, content, cookie)
		return res
	except Exception as e:
		print 'ERROR: %s' % e
		return res
	
def check(url, videoData=None, headers=None, cookie=None, doPrint=True, httpsskip=False):
	try:
		if 'google.com/file' in url:
			if videoData==None:
				videoData = getVideoMetaData(url, httpsskip)[0]
			
			if 'This+video+doesn%27t+exist' in videoData and 'Please+try+again+later' not in videoData:  
				log('FAIL', 'check', 'This video doesn\'t exist : %s' % url)
				return (False, videoData)
			
			res_split = videoData.split('&')
			for res in res_split:
				if 'status' in res:
					if 'fail' in res and 'Please+try+again+later' not in videoData:
						log('FAIL', 'check', 'status == fail')
						return (False, videoData)
		else:
			try:
				key_found = False
				http_res, red_url = client.request(url=url, output='responsecodeext', followredirect=True, headers=headers, cookie=cookie, IPv4=True, httpsskip=httpsskip)
				if http_res in client.HTTP_GOOD_RESP_CODES or http_res in client.GOOGLE_HTTP_GOOD_RESP_CODES_1:
					chunk = client.request(url=red_url, output='chunk', headers=headers, cookie=cookie, IPv4=True, httpsskip=httpsskip) # dont use web-proxy when retrieving chunk
					if doPrint:
						print "url --- %s" % red_url
						print "chunk --- %s" % chunk[0:50]
					
					for key in CONTAINER_KEYS:
						try:
							if key.lower() in str(chunk[0:20]).lower():
								key_found = True
								break
							if key.lower() in str(chunk[0:50]).lower():
								key_found = True
								break
						except:
							pass
				else:
					log('FAIL', 'check', 'HTTP Resp:%s for url: %s' % (http_res, url))
					return (False, videoData)
				if key_found == False:
					log('FAIL', 'check', 'keyword in chunk not found : %s --- Chunk: %s' % (url,chunk[0:20]))
					return (False, videoData)
			except:
				http_res, red_url, sz = client.simpleCheck(url, headers=headers, cookie=cookie)
				if http_res not in client.HTTP_GOOD_RESP_CODES and http_res not in client.GOOGLE_HTTP_GOOD_RESP_CODES_1:
					log('FAIL', 'check', 'HTTP Resp:%s for url: %s' % (http_res, url))
					return (False, videoData)

		return (True, videoData)
	except Exception as e:
		log('ERROR', 'check', '%s' % e, dolog=doPrint)
		return (False, videoData)
				
def getFileLink(id, httpsskip=False):

	st = time.time()
	durl = 'https://drive.google.com/uc?export=view&id=%s' % id
	fs = 0

	while 'drive.google.com' in durl and time.time() - st < 30:	
		#durl = 'https://drive.google.com/uc?export=view&id=0BxHDtiw8Swq7X0E5WUgzZTg2aE0'
		respD, headersD, contentD, cookieD = client.request(durl, output='extended')
		#print headers
		#print content
		#print cookieD
		try:
			fs = re.findall(r'</a> \((.*?)G\)', respD)[0]
			fs = int(float(fs.strip()) * (1024*1024*1024))
		except:
			try:
				fs = re.findall(r'</a> \((.*?)M\)', respD)[0]
				fs = int(float(fs.strip()) * (1024*1024))
			except:
				fs = 0
		confirm = re.findall(r'confirm.*?&', respD)[0]
		durl = 'https://drive.google.com/uc?export=download&%sid=%s' % (confirm,id)
		#print durl
		durl = client.request(durl, headers=headersD, cookie=cookieD, followredirect=True, output='geturl', limit='0')
		durl = durl.replace('?e=download','?e=file.mp4')
	
	res = True
	if 'drive.google.com' in durl:
		res = False
	
	return durl, res, fs

def urldata(url, videoData=None, usevideoData=False):
	ret = ''
	#print "urldata ----------- %s" % url
	if url != None and url == '':
		pass
	else:
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
							jsondata = {'label': qual, 'type': 'video/mp4', 'src': mfile, 'file': mfile, 'res': qual}
							jsondata = json.loads(json.dumps(jsondata))
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
		except Exception as e:
			print "Error in urldata"
			print "URL : %s" % url
			print e
		
	#print ret
	ret = json.dumps(ret, encoding='utf-8')
	#print "urldata ------ %s" % ret
	return client.b64encode(ret)
	
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
	
def rip_type(url, riptype):

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
		else:
			type = riptype
			
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
						
		elif 'blogspot.com' in url:
			try: qual = re.compile('=m(\d*)\?').findall(url)[0]
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
