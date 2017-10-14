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


import re,json,time
import os, sys
import js2py
from __builtin__ import ord

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

API_URL = 'https://api.openload.co/1'
PAIR_INFO_URL = API_URL + '/streaming/info'
GET_VIDEO_URL = API_URL + '/streaming/get?file=%s'
VALID_URL = r'https?://(?:openload\.(?:co|io)|oload\.tv)/(?:f|embed)/(?P<id>[a-zA-Z0-9-_]+)'

openloadhdr = {
	'User-Agent': client.USER_AGENT,
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}

name = 'openload'
	
class DecodeError(Exception):
    pass

class host:
	def __init__(self):
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
		testResults = self.test()
		self.working = testResults[0]
		self.msg = testResults[2]
		if self.working == False:
			self.captcha = True
			self.working = True
		self.resolver = True #self.test2()
		#workers.Thread(persistPairing, True).start()

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
			vidurl = None
			bool = False
			msg = []
			retmsg = ''
			for testUrl in testUrls:
				x1 = time.time()
				bool, p, retmsg, fs = check(testUrl, usePairing = False, embedpage=True)
				self.speedtest = time.time() - x1
				if bool == True:
					vidurl, err = resolve(testUrl)
					#vidurl = testUrl
					if vidurl != None:
						#print vidurl
						http_res = client.request(url=vidurl, output='responsecode')
						#print http_res
						if http_res not in client.HTTP_GOOD_RESP_CODES:
							bool = False
							
				msg.append([bool, testUrl, vidurl])
			return (bool, msg, retmsg)
		except Exception as e:
			return (False, e, str(e.args))
			
	def test2(self):
		try:
			testUrls = self.testUrl()
			links = []
			for testUrl in testUrls:
				links = self.createMeta(testUrl, 'Test', '', '720p', links, 'testing', 'BRRIP')
				print links
			if len(links) > 0:
				return True
		except Exception as e:
			self.log('ERROR', 'test2', e, dolog=True)
		return False

	def testUrl(self):
		#return ['https://openload.co/embed/kUEfGclsU9o','https://openload.co/f/tr6gjooZMj0/big_buck_bunny_240p_5mb.3gp.mp4']
		#return ['https://openload.co/f/tr6gjooZMj0/big_buck_bunny_240p_5mb.3gp.mp4']
		return ['https://openload.co/embed/kUEfGclsU9o']
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, vidtype='Movie', lang='en', sub_url=None, txt=''):
	
		url = url.replace('oload.tv','openload.co')
		urldata = client.b64encode(json.dumps('', encoding='utf-8'))
		params = client.b64encode(json.dumps('', encoding='utf-8'))
		
		if control.setting('use_openload_pairing') == True or control.setting('is_uss_installed') == False:
			isPairRequired = isPairingRequired(url)
			#print "isPairRequired %s" % isPairRequired
		else:
			isPairRequired = False
			
		vidurl, err = resolve(url, usePairing=False)
			
		pair = ''
		
		if isPairRequired == True:
			pair = ' *Pairing required* '
			if isPairingDone():
				pair = ' *Paired* '

		if vidurl == None:
			vidurl = url
			
		online, r1, r2, fs = check(vidurl, usePairing = False, embedpage=True)
		files_ret = []
		titleinfo = ''
		file_ext = '.mp4'

		try:
			files_ret.append({'source':self.name, 'maininfo':pair, 'titleinfo':titleinfo, 'quality':file_quality(vidurl, quality), 'vidtype':vidtype, 'rip':rip_type(vidurl, riptype), 'provider':provider, 'url':vidurl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'misc':{'pair':isPairRequired, 'player':'iplayer', 'gp':False}})
		except Exception as e:
			self.log('ERROR', 'createMeta', e, dolog=True)
			files_ret.append({'source':urlhost, 'maininfo':pair, 'titleinfo':titleinfo, 'quality':quality, 'vidtype':vidtype, 'rip':'Unknown' ,'provider':provider, 'url':vidurl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'misc':{'pair':isPairRequired, 'player':'eplayer', 'gp':False}})
			
		for fr in files_ret:
			links.append(fr)

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
		
def resolve(url, embedpage=False, usePairing=True):

	#control.log('[openload] - 1 %s' % url)
	try:
		bool, videoData, msg, fs = check(url,usePairing=usePairing) 
		if bool == False: 
			return (None, msg)
		if '/stream/' in url:
			return (url, msg)
		#control.log('[openload] - 2 %s' % url)
		id = re.compile('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)').findall(url)[0]
		embedpageURL = 'https://openload.co/embed/%s' % id
		
		if embedpage == True:
			return (embedpageURL, msg)

		videourl, videoData, msg = openloadS(embedpageURL, videoData=videoData, usePairing=usePairing)
		#control.log('[openload] - 2 %s' % videourl)

		return (videourl, msg)
	except Exception as e:
		e = '{}'.format(e)
		return (None, e)

def check(url, videoData=None, skipPageCheck=False, usePairing=True, embedpage=False, headers=None, cookie=None):
	try:
		retmsg = ''
		fs = 0
		
		ifstream = re.search('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)',(url)[0])
		if ifstream:
			return True

		if '/stream/' not in url:
			id = re.compile('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)').findall(url)[0]
			url = 'https://openload.co/embed/%s/' % id

			if skipPageCheck == False:
				if headers != None:
					for key in headers.keys():
						openloadhdr[key] = headers[key]

				videoData = client.request(url, headers=openloadhdr, cookie=cookie)
				if videoData == None:
					print '%s : File not found' % url
					log('ERROR', name, 'We can\'t find the file you are looking for. It maybe got deleted by the owner or was removed due a copyright violation. : %s' % url)
					return (False, videoData, 'File not found', fs)
				if 'File not found' in videoData or 'deleted by the owner' in videoData or 'Sorry!' in videoData: 
					print '%s : File not found' % url
					log('ERROR', name, 'We can\'t find the file you are looking for. It maybe got deleted by the owner or was removed due a copyright violation. : %s' % url)
					return (False, videoData, 'File not found', fs)
					
				try:
					fs = re.findall(r'window.filesize=(.*?);', videoData)[0]
				except:
					pass
					
				try:
					if fs == 0:
						vidData = client.request('https://oload.tv/f/%s/' % id, headers=openloadhdr, cookie=cookie)
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
					return (True, videoData, retmsg, fs)

			# if openloadS is success then the stream would be available
			result, videoData, retmsg = openloadS(url, videoData, usePairing=usePairing)
		else:
			result = url

		if result == None:
			if retmsg != '':
				log('ERROR', name, '%s : %s' % (retmsg, url))
			else:
				log('ERROR', name, 'File stream returned Null : %s' % url)
			return (False, videoData, retmsg, fs)
		
		return (checkVidPresence(result), videoData, retmsg, fs)
	except:
		return (False, videoData, retmsg, fs)
		
def checkVidPresence(streamurl, headers=None, cookie=None):
	http_res = client.request(url=streamurl, output='responsecode', headers=headers, cookie=cookie)
	if http_res in client.HTTP_GOOD_RESP_CODES:
		return True
	return False
		
def urldata(url, qual):

	try:
		mfile, err = resolve(url)
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

def openloadS(url, videoData=None, usePairing=True):
	try:
		ret_error = ''
		if videoData == None:
			videoData = getVideoMetaData(url=url)[0]

		video_id = match_id(url)
		ol_id = client.search_regex('<span[^>]+id="[^"]+"[^>]*>([0-9A-Za-z]+)</span>',videoData, 'openload ID')
		
		video_url = 'https://openload.co/stream/%s?mime=true'
		try:
			decoded = decode_id(ol_id)
			video_url = video_url % decoded
		except DecodeError as e:
			print('%s; falling back to method with evaluating' % e, video_id)
			try:
				decoded = eval_id_decoding(videoData, ol_id)
				video_url = video_url % decoded
			except DecodeError as e:
				try:
					if usePairing == True:
						print('%s; falling back to method with pairing' % e, video_id)
						title, video_url = pairing_method(video_id)
					else:
						print('%s; pairing is the only option available' % e, video_id)
						video_url = None
				except DecodeError as e:
					video_url = None
					ret_error = str(e)
					print ret_error

		return (video_url, videoData, ret_error)
	except Exception as e:
		ret_error = 'ERROR host_openload.py>openloadS: Args:%s Url:%s' % (e.args, url)
		print ret_error
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
	
def isPairingRequired(url):
	resolved_url, err = resolve(url=url, usePairing=False)
	
	if resolved_url != None:
		return False
	
	return True
	
def isPairingDone():
	
	pairurl = 'https://openload.co/pair'
	echourl = 'https://v4speed.oloadcdn.net/echoip'
	checkpairurl = 'https://openload.co/checkpair/%s'
	
	r = client.request(echourl, headers=openloadhdr)
	print "URL:%s  Resp:%s" % (echourl, r)
	
	checkpairurl_withip = checkpairurl % r
	r = client.request(checkpairurl_withip, headers=openloadhdr)
	
	#print r

	if r != None and '1' in r:
		return True
		
	return False

		
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
	
def log(type, name, msg):
	control.log('%s: %s %s' % (type, name, msg))
	
def logger(msg):
	control.log(msg)
