# -*- coding: utf-8 -*-

#########################################################################################################
#
# OpenLoad scrapper
#
# Coder Alpha
# https://github.com/coder-alpha
#
# Adapted from youtube-dl
# https://github.com/rg3/youtube-dl
# https://github.com/rg3/youtube-dl/issues/10408
# and modified for use with Plex Media Server
#

'''
    Specto Add-on
    Copyright (C) 2015 lambda

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


import re,json,time,base64
import os, sys
import js2py
from __builtin__ import ord, format

import traceback

try:
	from resources.lib.libraries import client
	from resources.lib.libraries import control
	from resources.lib.libraries import workers
except:
	# import sys, os
	# PATH = os.path.dirname(os.path.abspath(__file__)).split('resolvers')[0]
	# sys.path.insert(0, os.path.join(PATH,'libraries'))
	# import client
	# import control
	pass
	
try:
	import phantomjs
except:
	pass

API_URL = 'https://api.openload.co/1'
PAIR_INFO_URL = API_URL + '/streaming/info'
GET_VIDEO_URL = API_URL + '/streaming/get?file=%s'
VALID_URL = r'https?://(?:openload\.(?:co|io)|oload\.tv)/(?:f|embed)/(?P<id>[a-zA-Z0-9-_]+)'

USE_PHANTOMJS = True
USE_LOGIN_KEY = True
USE_PAIRING = True
USE_DECODING1 = False
USE_DECODING2 = False

USE_OPENLOAD_SUB = False

openloadhdr = {
	'User-Agent': client.USER_AGENT,
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}
	
TEST_VIDEO_IDS = ['kUEfGclsU9o','RQaodwqBjek','XDCUk2CA_U0','L-eIQjFctxQ','o3v8nnBhPDY','M2bsX_p_ptg','G-WGlQ_9cec','UiZLdKPsoL4','RQaodwqBjek','XDCUk2CA_U0','L-eIQjFctxQ']

name = 'openload'
loggertxt = []

class DecodeError(Exception):
    pass

class host:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Nov. 13, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.logo = 'http://i.imgur.com/OM7VzQs.png'
		self.name = 'openload'
		self.host = ['openload.io','openload.co','oload.tv']
		self.netloc = ['openload.io', 'openload.co', 'oload.tv']
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
		self.msg = testResults[2]
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
			bool = False
			testUrls = self.testUrl()
			vidurl = None
			msg = []
			retmsg = ''
			for testUrl in testUrls:
				x1 = time.time()
				bool, p, retmsg, fs, r1, sub_url = check(testUrl, usePairing = False, embedpage=True)
				self.speedtest = time.time() - x1
				if bool == True:
					vidurl, err, sub_url = resolve(testUrl)
					#vidurl = testUrl
					if vidurl != None or err != None and 'pair' in err.lower():
						#print vidurl
						if err != None and 'pair' in err.lower():
							vidurl = testUrl
						http_res = client.request(url=vidurl, output='responsecode')
						#print http_res
						if http_res not in client.HTTP_GOOD_RESP_CODES:
							bool = False
						else:
							bool = True
							break
							
				msg.append([bool, testUrl, vidurl])
			log(method='testWorking', err='%s online status: %s' % (self.name, bool))
			return (bool, msg, retmsg)
		except Exception as e:
			log(method='testWorking', err='%s online status: %s' % (self.name, bool))
			log(type='ERROR', method='testWorking', err=e)
			return (False, e, str(e.args))
			
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
		testUrls = []
		for v in TEST_VIDEO_IDS:
			testUrls.append('http://openload.co/f/%s' % v)
		return testUrls
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, vidtype='Movie', lang='en', sub_url=None, txt='', file_ext = '.mp4', testing=False):
	
		if testing == True:
			links.append(url)
			return links
			
		if control.setting('Host-%s' % name) == False:
			log('INFO','createMeta','Host Disabled by User')
			return links
			
		url = url.replace('oload.tv','openload.co').replace('/embed/','/f/')
		orig_url = url
		durl = url
		if testing == False:
			log(type='INFO',method='createMeta-1', err=u'creating meta for url: %s' % url)
		
		urldata = client.b64encode(json.dumps('', encoding='utf-8'))
		params = client.b64encode(json.dumps('', encoding='utf-8'))
		a1 = None
		
		if control.setting('use_openload_pairing') == True:
			isPairRequired, a1 = isPairingRequired(url)
			if isPairRequired == True:
				isPairRequired, a1 = isPairingRequired(url)
			#print "isPairRequired %s" % isPairRequired
		else:
			isPairRequired = False
			
		if a1 != None:
			vidurl = a1
		else:
			vidurl, err, sub_url_t = resolve(url, usePairing=False)
			if sub_url == None:
				sub_url = sub_url_t
			
		if vidurl != None:
			isPairRequired = False
			
		pair = ''
		
		if isPairRequired == True:
			pair = ' *Pairing required* '
			if isPairingDone():
				pair = ' *Paired* '
				
		if vidurl == None:
			vidurl = url
			
		online, r1, r2, fs, r3, sub_url_t = check(vidurl, usePairing=False, embedpage=True)
		if sub_url == None:
			sub_url = sub_url_t
		
		files_ret = []
		titleinfo = txt
		
		if testing == False:
			log(type='INFO',method='createMeta-2', err=u'pair: %s online: %s resolved url: %s' % (isPairRequired,online,vidurl))

		try:
			files_ret.append({'source':self.name, 'maininfo':pair, 'titleinfo':titleinfo, 'quality':file_quality(vidurl, quality), 'vidtype':vidtype, 'rip':rip_type(vidurl, riptype), 'provider':provider, 'url':vidurl, 'durl':durl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'misc':{'pair':isPairRequired, 'player':'iplayer', 'gp':False}})
		except Exception as e:
			log(type='ERROR',method='createMeta-3', err=u'%s' % e)
			files_ret.append({'source':urlhost, 'maininfo':pair, 'titleinfo':titleinfo, 'quality':quality, 'vidtype':vidtype, 'rip':'Unknown' ,'provider':provider, 'url':vidurl, 'durl':durl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'misc':{'pair':isPairRequired, 'player':'eplayer', 'gp':False}})
			
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
	
	
def getVideoMetaData(url):
	try:
		res = ('', '', '', '')
		
		result, headers, content, cookie = client.request(url, output = 'extended', headers=openloadhdr)
		return (result, headers, content, cookie)

	except Exception as e:
		print 'ERROR: %s' % e
		return res
		
def resolve(url, embedpage=False, usePairing=True, session=None):

	try:
		bool, videoData, msg, fs, result, sub_url = check(url, usePairing=usePairing, session=session) 
		if bool == False: 
			return (None, msg, sub_url)
		if '/stream/' in url or '.oloadcdn.' in url:
			return (url, msg, sub_url)
		if result != None and '/stream/' in result or '.oloadcdn.' in result:
			return (result, msg, sub_url)

		id = re.compile('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)').findall(url)[0]
		embedpageURL = 'https://openload.co/embed/%s' % id
		
		if embedpage == True:
			return (embedpageURL, msg, sub_url)

		videourl, videoData, msg = openloadS(embedpageURL, videoData=videoData, usePairing=usePairing, session=session)

		return (videourl, msg, sub_url)
	except Exception as e:
		e = '{}'.format(e)
		return (None, e, None)

def check(url, videoData=None, skipPageCheck=False, usePairing=True, embedpage=False, headers=None, cookie=None, session=None):
	try:
		retmsg = ''
		fs = 0
		result = None
		sub_url = None
		
		#ifstream = re.search('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)',(url)[0])
		#if ifstream:
		#	return True

		if '/stream/' not in url and '.oloadcdn.' not in url:
			id = re.compile('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)').findall(url)[0]
			url = 'https://openload.co/embed/%s/' % id

			if skipPageCheck == False:
				openloadhdrx = openloadhdr
				if headers != None:
					for key in headers.keys():
						openloadhdrx[key] = headers[key]

				videoData = client.request(url, headers=openloadhdrx, cookie=cookie)
				if videoData == None:
					print '%s : File not found' % url
					log(type='FAIL', method='check', err='File deleted by the owner or was removed. : %s' % url)
					return (False, videoData, 'File not found', fs, None, sub_url)
				if 'File not found' in videoData or 'deleted by the owner' in videoData or 'Sorry!' in videoData: 
					print '%s : File not found' % url
					log(type='FAIL', method='check', err='File deleted by the owner or was removed. : %s' % url)
					return (False, videoData, 'File not found', fs, None, sub_url)
					
				try:
					fs = re.findall(r'window.filesize=(.*?);', videoData)[0]
				except:
					pass
					
				if USE_OPENLOAD_SUB == True:
					try:
						sub_url_t = re.findall(r'suburl = \"(.*?)\";', videoData)[0]
						sub_url_t = sub_url_t.replace('\\','')
						sub_url_t = client.request(sub_url_t, headers=openloadhdrx, cookie=cookie)
						if len(sub_url_t) > 50:
							sub_url = sub_url_t
					except:
						sub_url = None
					
				try:
					if fs == 0:
						vidData = client.request('https://openload.co/f/%s/' % id, headers=openloadhdr, cookie=cookie)
						#print vidData
						respD = client.parseDOM(vidData, 'div', attrs={'class': 'content-text'})[0]
						#print respD
						fs = re.findall(r':\ (.*?)\ ', respD)[0]
						if 'gb' in respD.lower():
							fs = int(float(fs.strip()) * (1024*1024*1024))
						else:
							fs = int(float(fs.strip()) * (1024*1024))
				except:
					pass
					
				if embedpage == True:
					return (True, videoData, retmsg, fs, None, sub_url)

			# if openloadS is success then the stream would be available
			result, videoData, retmsg = openloadS(url, videoData, usePairing=usePairing, session=session)
		else:
			result = url
			try:
				fs = client.getFileSize(url)
			except:
				fs = 0

		if result == None:
			if retmsg != '':
				log(type='FAIL', method='check', err='%s : %s' % (retmsg, url))
			return (False, videoData, retmsg, fs, result, sub_url)
		
		if fs > 0:
			return (True, videoData, retmsg, fs, result, sub_url)
		else:
			return (checkVidPresence(result), videoData, retmsg, fs, result, sub_url)
	except:
		return (False, videoData, retmsg, fs, result, sub_url)
		
def checkVidPresence(streamurl, headers=None, cookie=None):
	http_res = client.request(url=streamurl, output='responsecode', headers=headers, cookie=cookie)
	if http_res in client.HTTP_GOOD_RESP_CODES:
		return True
	return False
		
def urldata(url, qual):

	try:
		mfile, err, sub_url = resolve(url)
		files = []
		jsondata = {
					"label": qual,
					"type": "video/mp4",
					"src": mfile,
					"file": mfile,
					"res": qual
				}
		files.append(jsondata)
		#print files
		ret = json.dumps(files, encoding='utf-8')
		#print "urldata ------ %s" % ret
		return client.b64encode(ret)
	except:
		return client.b64encode(json.dumps('', encoding='utf-8'))
	
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
	
def file_quality(url, quality):
	#print "%s - %s" % (self.name, url)
	
	try:
		if '1080' in url:
			return '1080p'
		elif '720' in url:
			return '720p'
		elif '480' in url:
			return '480p'
		elif '360' in url:
			return '360p'
		else:
			return unicode(quality)
	except:
		return unicode(quality)		

def openloadS(url, videoData=None, usePairing=True, session=None):
	try:
		ret_error = ''
		if videoData == None:
			videoData = client.request(url, headers=openloadhdr)
			
		try:
			ol_id = client.search_regex('<span[^>]+id="[^"]+"[^>]*>([0-9A-Za-z]+)</span>',videoData, 'openload ID')
		except:
			ol_id = None
		try:
			video_id = match_id(url)
		except:
			video_id = None
		log(type='INFO',method='openloadS', err=u'OpenLoad iD: %s' % video_id)
		video_url = None
		e = ''
		try:
			if USE_PHANTOMJS == True and (session == None or control.setting('%s-%s' % (session, 'Use-PhantomJS')) == True) and control.setting('use_phantomjs') == True:
				log(type='INFO',method='openloadS', err=u'trying phantomjs method: %s' % (video_id))
				try:
					v_url, bool = phantomjs.decode(url)
					if bool == False:
						ret_error = v_url
						raise DecodeError(ret_error)
					else:
						video_url = v_url
						ret_error = ''
						log(type='SUCCESS',method='openloadS', err=u'*PhantomJS* method is working: %s' % video_id)
				except:
					raise DecodeError('phantomjs not working')
			else:
				raise DecodeError('phantomjs is disabled')
		except DecodeError as e:
			try:
				if USE_LOGIN_KEY == True and video_url == None:
					log(type='INFO',method='openloadS', err=u'%s; trying L/K API method: %s' % (e,video_id))
					v_url, cont, cu, dlk, ret_error = link_from_api(video_id)
					if v_url == None:
						raise DecodeError('%s' % ret_error)
					else:
						ret_error = ''
						video_url = v_url
						log(type='SUCCESS',method='openloadS', err=u'*L/K API* method is working: %s' % video_id)
				else:
					raise DecodeError('L/K method disabled via hard coded option')
			except DecodeError as e:
				if USE_DECODING1 == True and video_url == None:
					log(type='INFO',method='openloadS', err=u'%s; falling back to decode_id method: %s' % (e,video_id))
					try:
						v_url = 'https://openload.co/stream/%s?mime=true'
						decoded = decode_id(ol_id)
						video_url = v_url % decoded
					except DecodeError as e:
						pass
				if USE_DECODING2 == True and video_url == None:
					log(type='INFO',method='openloadS', err=u'%s; falling back to method with evaluating: %s' % (e,video_id))
					try:
						decoded = eval_id_decoding(videoData, ol_id)
						video_url = video_url % decoded
					except DecodeError as e:
						pass
				if USE_PAIRING == True:
					try:
						if usePairing == True and video_url == None:
							log(type='INFO',method='openloadS', err=u'%s; falling back to method with pairing: %s' % (e,video_id))
							title, video_url = pairing_method(video_id)
							if video_url == None:
								raise DecodeError('Pairing not working')
							ret_error = ''
							log(type='SUCCESS',method='openloadS', err=u'*Pairing* method is working: %s' % video_id)
						elif video_url == None:
							ret_error = 'pairing is the only option available'
							log(type='INFO',method='openloadS', err=u'%s; %s : %s' % (e,ret_error,video_id))
							video_url = None
						elif video_url != None:
							ret_error = ''
					except DecodeError as e:
						video_url = None
						ret_error = str(e)
						print ret_error

		return (video_url, videoData, ret_error)
	except Exception as e:
		ret_error = '%s ID:%s' % (e, video_id)
		log(type='ERROR',method='openloadS', err=u'%s: %s' % (e, video_id))
		
		return (None, videoData, ret_error)
		
#############################################################################################
# Adapter by Coder-Alpha from:
# Credit: https://github.com/Tithen-Firion
# https://github.com/Tithen-Firion/youtube-dl/blob/openload-fix-that-cant-be-merged/youtube_dl/extractor/openload.py
#############################################################################################

def decode_id(ol_id):
	try:
		# raise # uncomment to test method with evaluating
		decoded = ''
		a = ol_id[-40:]
		b = []
		for i in range(0, len(a), 8):
			b.append(int(a[i:i + 8] or '0', 16))
		ol_id = ol_id[:-40]
		j = 0
		k = 0
		while j < len(ol_id):
			c = 128
			d = 0
			e = 0
			f = 0
			_more = True
			while _more:
				if j + 1 >= len(ol_id):
					c = 143
				f = int(ol_id[j:j + 2] or '0', 16)
				j += 2
				d += (f & 127) << e
				e += 7
				_more = f >= c
			g = d ^ b[k % 5]
			for i in range(4):
				char_dec = (g >> 8 * i) & (c + 127)
				char = compat_chr(char_dec)
				if char != '#':
					decoded += char
			k += 1
		decoded.encode('utf8').decode('ascii') # test if it's ascii string
		print "decoded %s" % decoded
		return decoded
	except:
		raise DecodeError('Could not decode ID')


def eval_id_decoding(videoData, ol_id):
	try:
		# raise # uncomment to test method with pairing
		# js_code = client.search_regex(
			# r"(ﾟωﾟﾉ=.*?\('_'\);.*?)ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //\*´∇｀\*/ \['_'\];",
			# videoData, 'openload decrypt code', flags=re.S)
		# js_code = re.sub('''if\s*\([^\}]+?typeof[^\}]+?\}''', '', js_code)
		
		js_code = client.search_regex(r"(ﾟωﾟﾉ=.*?\('_'\);.*?)ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //\*´∇｀\*/ \['_'\];",videoData, 'openload decrypt code', flags=re.S)
		decoder = js_code.split("('_');")[-1]
		js_code = re.sub('''if\s*\([^\}]+?typeof[^\}]+?\}''', '', js_code)
	except:
		raise DecodeError('Error: Could not find JavaScript')

	js_code = '''
            var id = "%s"
              , decoded
              , document = {}
              , window = this
              , $ = function(){
                  return {
                    text: function(a){
                      if(a)
                        decoded = a;
                      else
                        return id;
                    },
                    ready: function(a){
                      a()
                    }
                  }
                };
            (function(d, w){
              var f = function(){};
              var s = '';
              var o = null;
              var b = false;
              var n = 0;
              var df = ['close','createAttribute','createDocumentFragment','createElement','createElementNS','createEvent','createNSResolver','createRange','createTextNode','createTreeWalker','evaluate','execCommand','getElementById','getElementsByName','getElementsByTagName','importNode','open','queryCommandEnabled','queryCommandIndeterm','queryCommandState','queryCommandValue','write','writeln'];
              df.forEach(function(e){d[e]=f;});
              var do_ = ['anchors','applets','body','defaultView','doctype','documentElement','embeds','firstChild','forms','images','implementation','links','location','plugins','styleSheets'];
              do_.forEach(function(e){d[e]=o;});
              var ds = ['URL','characterSet','compatMode','contentType','cookie','designMode','domain','lastModified','referrer','title'];
              ds.forEach(function(e){d[e]=s;});
              var wb = ['closed','isSecureContext'];
              wb.forEach(function(e){w[e]=b;});
              var wf = ['addEventListener','alert','atob','blur','btoa','cancelAnimationFrame','captureEvents','clearInterval','clearTimeout','close','confirm','createImageBitmap','dispatchEvent','fetch','find','focus','getComputedStyle','getSelection','matchMedia','moveBy','moveTo','open','postMessage','print','prompt','releaseEvents','removeEventListener','requestAnimationFrame','resizeBy','resizeTo','scroll','scrollBy','scrollTo','setInterval','setTimeout','stop'];
              wf.forEach(function(e){w[e]=f;});
              var wn = ['devicePixelRatio','innerHeight','innerWidth','length','outerHeight','outerWidth','pageXOffset','pageYOffset','screenX','screenY','scrollX','scrollY'];
              wn.forEach(function(e){w[e]=n;});
              var wo = ['applicationCache','caches','crypto','external','frameElement','frames','history','indexedDB','localStorage','location','locationbar','menubar','navigator','onabort','onanimationend','onanimationiteration','onanimationstart','onbeforeunload','onblur','oncanplay','oncanplaythrough','onchange','onclick','oncontextmenu','ondblclick','ondevicemotion','ondeviceorientation','ondrag','ondragend','ondragenter','ondragleave','ondragover','ondragstart','ondrop','ondurationchange','onemptied','onended','onerror','onfocus','onhashchange','oninput','oninvalid','onkeydown','onkeypress','onkeyup','onlanguagechange','onload','onloadeddata','onloadedmetadata','onloadstart','onmessage','onmousedown','onmouseenter','onmouseleave','onmousemove','onmouseout','onmouseover','onmouseup','onoffline','ononline','onpagehide','onpageshow','onpause','onplay','onplaying','onpopstate','onprogress','onratechange','onreset','onresize','onscroll','onseeked','onseeking','onselect','onshow','onstalled','onstorage','onsubmit','onsuspend','ontimeupdate','ontoggle','ontransitionend','onunload','onvolumechange','onwaiting','onwebkitanimationend','onwebkitanimationiteration','onwebkitanimationstart','onwebkittransitionend','onwheel','opener','parent','performance','personalbar','screen','scrollbars','self','sessionStorage','speechSynthesis','statusbar','toolbar','top'];
              wo.forEach(function(e){w[e]=o;});
              var ws = ['name'];
              ws.forEach(function(e){w[e]=s;});
            })(document, window);
            %s;
            decoded;''' % (ol_id, js_code)

	try:
		ret = js2py.eval_js(js_code)
		if ret == '':
			raise DecodeError('Error: Returned null response')
		for char in ret:
			if re.match(r'''[^\w\-\.~:\[\]@!$'()*+,;=`]''', char):
				raise DecodeError('Error: Match error')
		try:
			ret.encode('utf8').decode('ascii') # test if it's ascii string
		except:
			raise DecodeError('Error: Decoding to ASCII')
		if 'API' in ret:
			raise DecodeError('Error: JavaScript returned use API warning message')
		return ret
	except:
		#print "*** print_exc:"
		#traceback.print_exc()
		raise DecodeError('Error: Could not eval ID decoding')
		
def pairing_method(video_id):
	#persistPairing()
	
	get_info = client.request(GET_VIDEO_URL % video_id, headers=openloadhdr)
	#print "get_info --- %s" % get_info
	get_info = json.loads(get_info)
	status = get_info.get('status')
	#print "status --- %s" % status
	if status == 200:
		result = get_info.get('result', {})
		return result.get('name'), result.get('url')
	elif status == 403:
		pair_info = client.request(PAIR_INFO_URL, headers=openloadhdr)
		#print "pair_info --- %s" % pair_info
		pair_info = json.loads(pair_info)
		if pair_info.get('status') == 200:
			pair_url = pair_info.get('result', {}).get('auth_url')
			if pair_url:
				#print 'Open this url: %s, solve captcha, click "Pair" button and try again' % pair_url
				raise DecodeError('Open this url: %s, solve captcha, click "Pair" button and try again' % pair_url)
			else:
				#print 'Pair URL not found'
				raise DecodeError('Pair URL not found: %s' % video_id)
		else:
			#print 'Error loading pair info'
			raise DecodeError('Error loading pair info: %s' % video_id)
	else:
		#print 'Error loading JSON metadata'
		msg = get_info.get('msg')
		raise DecodeError('Error %s - %s: %s' % (status, msg, video_id))
		
#############################################################################################

try:
	compat_chr = unichr  # Python 2
except NameError:
	compat_chr = chr
	
def match_id(url):
	VALID_URL_RE = re.compile(VALID_URL)
	m = VALID_URL_RE.match(url)
	assert m
	return m.group('id')
	
def isPairingRequired(url, session=None):
	resolved_url, err, sub_url = resolve(url=url, usePairing=False, session=session)
	
	if resolved_url != None:
		return False, resolved_url
	
	return True, resolved_url
	
def isPairingDone():
	
	pairurl = 'https://openload.co/pair'
	echourl = 'https://v4speed.oloadcdn.net/echoip'
	checkpairurl = 'https://openload.co/checkpair/%s'
	
	r = client.request(echourl, headers=openloadhdr)
	
	checkpairurl_withip = checkpairurl % r
	r = client.request(checkpairurl_withip, headers=openloadhdr)
	
	if r != None and '1' in r:
		return True
		
	return False
	
def unpair():

	c = 0
	
	myLog = []
	
	if isPairingDone() == True:
	
		msg = 'System is paired. Continuing unpair routine.'
		myLog.append(msg)
		
		try:
			while isPairingDone() == True and c < 25:
				for i in range(0, len(TEST_VIDEO_IDS)):	
					msg = 'UnPair attempt %s' % str(c*len(TEST_VIDEO_IDS)+i)
					myLog.append(msg)
					title, video_url = pairing_method(TEST_VIDEO_IDS[i])
					msg = 'Title: %s Url: %s' % (title, video_url)

					if video_url == None:
						raise DecodeError('Null video_url')
					
					time.sleep(0.2)
				c += 1
		except DecodeError as e:
			print e
			msg = 'System should now be UnPaired'
			myLog.append(msg)
			
	else:
		msg = 'System is not paired'
		myLog.append(msg)
		
	return myLog
		
	
# Twoure's API method
def link_from_api(fid, lk=None, test=False):
	
	lk = control.setting('control_openload_api_key')
	lk = lk.split(':')
	l = lk[0]
	k = lk[1]
	burl = 'https://api.openload.co/1/file/'
	
	msg = ''
	cont = True
	captcha_url = None
	dlticket = None
	
	try:
		if 'http' in fid:
			fid = match_id(fid)
			
		url = None
		url = burl + 'dlticket?file=' + fid + '&login=' + l + '&key=' + k
		data = client.request(url)
		data = json.loads(data)
	except Exception as e:
		msg = str(e)
		print e
		log(type='FAIL', method='link_from_api', err='cannot handle 1st api link %s' % url)
		return None, cont, captcha_url, dlticket, msg

	if data["status"] == 200:
		dlticket = data["result"]["ticket"]
		if 'captcha_url' in data["result"].keys():
			captcha_url = data["result"]["captcha_url"]
			if captcha_url != None and captcha_url != False:
				captcha_url = captcha_url.replace('://',':||').replace('//','/').replace(':||','://')
				#captcha_url = 'https://rsz.io/%s?w=300&h=300' % captcha_url.split('//')[1]
				log(type='INFO', method='link_from_api', err='captcha url %s' % captcha_url)
			
		if test == True:
			captcha_url = 'https://openload.co/dlcaptcha/QdCRoYF8wouT3YSj.png'

		try:
			url = None
			url = burl + 'dl?file=' + fid + '&ticket=' + dlticket
			data = client.request(url)
			data = json.loads(data)
			#print data
			msg = data["msg"]
			if data["status"] == 200:
				return data['result']['url'].replace("https", "http"), cont, captcha_url, dlticket, msg
			else:
				log(type='FAIL', method='link_from_api', err='cannot handle 2nd api link %s' % data['msg'])
		except:
			log(type='FAIL', method='link_from_api', err='cannot handle 2nd api link %s' % url)
	else:
		msg = data["msg"]
		log(type='FAIL', method='link_from_api', err='>>> %s' % msg)

	return None, cont, captcha_url, dlticket, msg
	
######################################################################################
def SolveCaptcha(captcha_response, fid, dlticket):
	
	burl = 'https://api.openload.co/1/file/'
	try:
		if 'http' in fid:
			fid = match_id(fid)
			
		url = None
		url = burl + 'dl?file=' + fid + '&ticket=' + dlticket + '&captcha_response=' + captcha_response
		data = client.request(url)
		data = json.loads(data)

		if data["status"] == 200:
			return data['result']['url'].replace("https", "http")
		else:
			log(type='FAIL', method='SolveCaptcha', err='cannot handle 2nd api link >>> %s' % data['msg'])
	except:
		log(type='ERROR', method='SolveCaptcha', err='cannot handle 2nd api link %s' % url)

	return None
		
def persistPairing(runIndefinite=False):
	pairurl = 'https://openload.co/pair'
	echourl = 'https://v4speed.oloadcdn.net/echoip'
	checkpairurl = 'https://openload.co/checkpair/%s'
	
	r = client.request(echourl, headers=openloadhdr)
	print "URL:%s  Resp:%s" % (echourl, r)
	
	checkpairurl_withip = checkpairurl % r
	r = client.request(checkpairurl_withip, headers=openloadhdr)
	print "URL:%s  Resp:%s" % (checkpairurl_withip, r)
	
	if runIndefinite == True:
		while True:
			time.sleep(5*60) # 5 min. loop refresh
			r = client.request(checkpairurl_withip, headers=openloadhdr)
			print "URL:%s  Resp:%s" % (checkpairurl_withip, r)

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
