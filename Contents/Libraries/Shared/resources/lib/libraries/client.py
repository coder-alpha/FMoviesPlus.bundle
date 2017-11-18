# -*- coding: utf-8 -*-

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

import re,sys,urllib2,HTMLParser,urllib,urlparse
import random, time, cookielib
import base64
import traceback
import httplib
import requests

from resources.lib.libraries import cache
from resources.lib.libraries import control
from resources.lib.libraries import workers

from __builtin__ import eval


#-------------------------------------------------------------------------------------------------------------
# Enforce IPv4 for GetlinkAPI nks Google li
# do this once at program startup
# Reference: http://stackoverflow.com/questions/2014534/force-python-mechanize-urllib2-to-only-use-a-requests
#--------------------
import socket
origGetAddrInfo = socket.getaddrinfo

def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
	return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)

# #replace the original socket.getaddrinfo by our version
# socket.getaddrinfo = getAddrInfoWrapper
# socket.has_ipv6 = False
#-------------------------------------------------------------------------------------------------------------

# --- SSL fixes.

def fix_ssl():
	# This solves the HTTP connection problem on Ubuntu Lucid (10.04):
	#	 SSLError: [Errno 1] _ssl.c:480: error:140770FC:SSL routines:SSL23_GET_SERVER_HELLO:unknown protocol
	# It also fixes the following problem with StaticPython ob some systems:
	#	 SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:590)
	#
	# This fix works with Python version 2.4--2.7, with the bundled and the new
	# (1.16) ssl module.
	class fake_ssl:
		import ssl	# Needed, the MEGA API is https:// only.
		def partial(func, *args, **kwds):	# Emulate functools.partial for 2.4.
			return lambda *fargs, **fkwds: func(*(args+fargs), **dict(kwds, **fkwds))
		wrap_socket = staticmethod(partial(
				ssl.wrap_socket, ssl_version=ssl.PROTOCOL_TLSv1))
		# Prevent staticpython from trying to load /usr/local/ssl/cert.pem .
		# `export PYTHONHTTPSVERIFY=1' would also work from the shell.
		if getattr(ssl, '_create_unverified_context', None):
			_create_default_https_context = staticmethod(
					ssl._create_unverified_context)
		del ssl, partial
	httplib.ssl = fake_ssl

def shrink_host(url):
	u = urlparse.urlparse(url)[1].split('.')
	u = u[-2] + '.' + u[-1]
	return u.encode('utf-8')

GLOBAL_TIMEOUT_FOR_HTTP_REQUEST = 15
HTTP_GOOD_RESP_CODES = ['200','206']
GOOGLE_HTTP_GOOD_RESP_CODES_1 = ['429']
	
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0"
IE_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko'
FF_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
OPERA_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 OPR/34.0.2036.50'
IOS_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
ANDROID_USER_AGENT = 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'
#SMU_USER_AGENT = 'URLResolver for Kodi/%s' % (addon_version)

IP_OVERIDE = True

def request(url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, use_web_proxy=False, XHR=False, IPv4=False):

# output extended = 4, response = 2, responsecodeext = 2
	
	try:
		handlers = []
		redirectURL = url
		
		if IPv4 == True:
			setIP4()
			
		if error==False and not proxy == None:
			handlers += [urllib2.ProxyHandler({'http':'%s' % (proxy)}), urllib2.HTTPHandler]
			opener = urllib2.build_opener(*handlers)
			opener = urllib2.install_opener(opener)

		if error==False and output == 'cookie2' or output == 'cookie' or output == 'extended' or not close == True:
			cookies = cookielib.LWPCookieJar()
			if httpsskip or use_web_proxy:
				handlers += [urllib2.HTTPHandler(), urllib2.HTTPCookieProcessor(cookies)]
			else:
				handlers += [urllib2.HTTPHandler(), urllib2.HTTPSHandler(), urllib2.HTTPCookieProcessor(cookies)]
			opener = urllib2.build_opener(*handlers)
			opener = urllib2.install_opener(opener)
			
		try:
			if error==False:
				if sys.version_info < (2, 7, 9): raise Exception()
				import ssl; ssl_context = ssl.create_default_context()
				ssl_context.check_hostname = False
				ssl_context.verify_mode = ssl.CERT_NONE
				handlers += [urllib2.HTTPSHandler(context=ssl_context)]
				opener = urllib2.build_opener(*handlers)
				opener = urllib2.install_opener(opener)
		except:
			pass

		try: headers.update(headers)
		except: headers = {}
		if 'User-Agent' in headers:
			pass
		elif not mobile == True:
			#headers['User-Agent'] = agent()
			#headers['User-Agent'] = Constants.USER_AGENT
			headers['User-Agent'] = randomagent()		
		else:
			headers['User-Agent'] = 'Apple-iPhone/701.341'
		if 'Referer' in headers:
			pass
		elif referer == None:
			try:
				headers['Referer'] = '%s://%s/' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)
			except:
				try:
					headers['Referer'] = url
				except:
					pass
		else:
			headers['Referer'] = referer
		if not 'Accept-Language' in headers:
			headers['Accept-Language'] = 'en-US'
		if 'X-Requested-With' in headers:
			pass
		elif XHR == True:
			headers['X-Requested-With'] = 'XMLHttpRequest'
		if 'Cookie' in headers:
			pass
		elif not cookie == None:
			headers['Cookie'] = cookie

		if error==False and redirect == False:
			class NoRedirection(urllib2.HTTPErrorProcessor):
				def http_response(self, request, response): 
					if IPv4 == True:
						setIP6()
					return response

			opener = urllib2.build_opener(NoRedirection)
			opener = urllib2.install_opener(opener)

			try: del headers['Referer']
			except: pass
			
		redirectHandler = None
		urlList = []
		if error==False and followredirect:
			class HTTPRedirectHandler(urllib2.HTTPRedirectHandler):
				def redirect_request(self, req, fp, code, msg, headers, newurl):
					newreq = urllib2.HTTPRedirectHandler.redirect_request(self,
						req, fp, code, msg, headers, newurl)
					if newreq is not None:
						self.redirections.append(newreq.get_full_url())
					if IPv4 == True:
						setIP6()
					return newreq
			
			redirectHandler = HTTPRedirectHandler()
			redirectHandler.max_redirections = 10
			redirectHandler.redirections = [url]

			opener = urllib2.build_opener(redirectHandler)
			opener = urllib2.install_opener(opener)

		request = urllib2.Request(url, data=post, headers=headers)
		#print request

		try:
			response = urllib2.urlopen(request, timeout=int(timeout))
			if followredirect:
				for redURL in redirectHandler.redirections:
					urlList.append(redURL) # make a list, might be useful
					redirectURL = redURL
					
		except urllib2.HTTPError as response:
			
			try:
				resp_code = response.code
			except:
				resp_code = None
			
			try:
				content = response.read()
			except:
				content = ''
				
			if response.code == 503:
				#Log("AAAA- CODE %s|%s " % (url, response.code))
				if 'cf-browser-verification' in content:
					control.log('cf-browser-verification: CF-OK')
					
					netloc = '%s://%s' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)
					#cf = cache.get(cfcookie, 168, netloc, headers['User-Agent'], timeout)
					cfc = cfcookie()
					cf = cfc.get(netloc, headers['User-Agent'], timeout)
					
					headers['Cookie'] = cf
					request = urllib2.Request(url, data=post, headers=headers)
					response = urllib2.urlopen(request, timeout=int(timeout))
				elif error == False:
					if IPv4 == True:
						setIP6()
					return
				elif error == True:
					return '%s: %s' % (response.code, response.reason), content
			elif response.code == 403:
				if output == 'response':
					return response.code, content
				else:
					return
			elif response.code == 307:
				#Log("AAAA- Response read: %s" % response.read(5242880))
				#Log("AAAA- Location: %s" % (response.headers['Location'].rstrip()))
				cookie = ''
				try: cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
				except: pass
				headers['Cookie'] = cookie
				request = urllib2.Request(response.headers['Location'], data=post, headers=headers)
				response = urllib2.urlopen(request, timeout=int(timeout))
				#Log("AAAA- BBBBBBB %s" %  response.code)
			elif resp_code != None:
				if IPv4 == True:
					setIP6()
				if output == 'response':
					return (resp_code, None)
				return resp_code
			elif error == False:
				#print ("Response code",response.code, response.msg,url)
				if IPv4 == True:
					setIP6()
				return
			else:
				if IPv4 == True:
					setIP6()
				return
		except Exception as e:
			control.log('ERROR client.py>request : %s' % url)
			control.log('ERROR client.py>request : %s' % e.args)
			if IPv4 == True:
				setIP6()
			if output == 'response':
				return (None, None)
			return None

		if output == 'cookie':
			try: result = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
			except: pass
			try: result = cf
			except: pass

		elif output == 'response':
			if limit == '0':
				result = (str(response.code), response.read(224 * 1024))
			elif not limit == None:
				result = (str(response.code), response.read(int(limit) * 1024))
			else:
				result = (str(response.code), response.read(5242880))
				
		elif output == 'responsecodeext':
			result = (str(response.code),redirectURL)
			
		elif output == 'responsecode':
			result = str(response.code)

		elif output == 'chunk':
			try: content = int(response.headers['Content-Length'])
			except: content = (2049 * 1024)
			#Log('CHUNK %s|%s' % (url,content))
			if content < (2048 * 1024):
				if IPv4 == True:
					setIP6()
				return
			result = response.read(16 * 1024)
			if close == True: response.close()
			if IPv4 == True:
				setIP6()
			return result

		elif output == 'extended':
			try: cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
			except: pass
			try: cookie = cf
			except: pass
			content = response.headers
			result = response.read(5242880)
			if IPv4 == True:
				setIP6()
			return (result, headers, content, cookie)

		elif output == 'geturl':
			result = response.geturl()

		elif output == 'headers':
			content = response.headers
			if IPv4 == True:
				setIP6()
			return content

		else:
			if limit == '0':
				result = response.read(224 * 1024)
			elif not limit == None:
				result = response.read(int(limit) * 1024)
			else:
				result = response.read(5242880)

		if close == True:
			response.close()

		if IPv4 == True:
			setIP6()
		return result
		
	except Exception as e:
		control.log('ERROR client.py>request %s, %s' % (e.args,url))
		traceback.print_exc()
		if IPv4 == True:
			setIP6()
		return
		
def simpleCheck(link, headers={}, cookie={}, retError=False, retry429=False, cl=3):
	try:
		code = '0'
		size = '0'
		red_url = None 
		r = requests.get(link, headers=headers, cookies=cookie, stream=True, verify=False, allow_redirects=True)
		
		if retry429 == True:
			c = 0
			while r.status_code == 429 and c < cl:
				time.sleep(5)
				r = requests.get(link, stream=True, verify=False, allow_redirects=True)
				c += 1
		
		if str(r.status_code) not in HTTP_GOOD_RESP_CODES and str(r.status_code) not in GOOGLE_HTTP_GOOD_RESP_CODES_1:
			raise Exception('HTTP Response: %s' % str(r.status_code))
		size = r.headers['Content-length']
		red_url = r.url
		code = str(r.status_code)
		r.close()
		
		#site = urllib.urlopen(link)
		#meta = site.info()
		#size = meta.getheaders("Content-Length")[0]
		
		if retError == True:
			return code, red_url, size, ''
		else:
			return code, red_url, size
	except Exception as e:
		if retError == True:
			return code, red_url, size, '{}'.format(e)
		else:
			return code, red_url, size
		
def getFileSize(link, retError=False, retry429=False, cl=3):
	try:
		r = requests.get(link, stream=True, verify=False, allow_redirects=True)
		
		if retry429 == True:
			c = 0
			while r.status_code == 429 and c < cl:
				time.sleep(5)
				r = requests.get(link, stream=True, verify=False, allow_redirects=True)
				c += 1
		
		if str(r.status_code) not in HTTP_GOOD_RESP_CODES and str(r.status_code) not in GOOGLE_HTTP_GOOD_RESP_CODES_1:
			raise Exception('HTTP Response: %s' % str(r.status_code))
		size = r.headers['Content-length']
		r.close()
		
		#site = urllib.urlopen(link)
		#meta = site.info()
		#size = meta.getheaders("Content-Length")[0]
		
		if retError == True:
			return size, ''
		else:
			return size
	except Exception as e:
		if retError == True:
			return 0, '{}'.format(e)
		else:
			return 0
		
def send_http_request(url, data=None, timeout=None, fix_ssl=True):
	"""Return a httplib.HTTPResponse object."""
	#print url
	#print data
	if fix_ssl == True:
		fix_ssl()
		pass
		
	match = URL_RE.match(url)
	if not match:
		raise ValueError('Bad URL: %s' % url)
	schema = match.group(1)
	if schema not in ('http', 'https'):
		raise ValueError('Unknown schema: %s' % schema)
	host = match.group(2)
	if match.group(3):
		port = int(match.group(3))
	else:
		port = (80, 443)[schema == 'https']
	path = url[match.end():] or '/'

	#print host
	ipaddr = socket.gethostbyname(host)	# Force IPv4. Needed by Mega.
	#print ipaddr
	hc_cls = (httplib.HTTPConnection, httplib.HTTPSConnection)[schema == 'https']
	# TODO(pts): Cleanup: Call hc.close() eventually.
	if sys.version_info < (2, 6):	# Python 2.5 doesn't support timeout.
		hc = hc_cls(ipaddr, port)
	else:
		hc = hc_cls(ipaddr, port, timeout=timeout)
	if data is None:
		hc.request('GET', path)
	else:
		hc.request('POST', path, data)
	return hc.getresponse()	# HTTPResponse.
		
def getPageDataBasedOnOutput(res, output):

	if res == None:
		page_data_string = None
	else:
		if output == 'extended':
			page_data_string, headers, content, cookie = res
		elif output == 'response' or output == 'responsecodeext':
			resp_code, page_data_string = res
		else:
			page_data_string = res
		
	return page_data_string
	
def getResponseDataBasedOnOutput(page_data_string, res, output):
	if output == 'extended':
		x, headers, content, cookie = res
		return (page_data_string, headers, content, cookie)
	elif output == 'response' or output == 'responsecodeext':
		resp_code, x = res
		return (resp_code, page_data_string)
	else:
		return page_data_string

def setIP4(setoveride=False):

	if setoveride==False and IP_OVERIDE == True:
		return
	#replace the original socket.getaddrinfo by our version
	socket.getaddrinfo = getAddrInfoWrapper
	socket.has_ipv6 = False
	
def setIP6(setoveride=False):

	if setoveride==False and IP_OVERIDE == True:
		return
	#replace the IP4 socket.getaddrinfo by original
	socket.getaddrinfo = origGetAddrInfo
	socket.has_ipv6 = True
	
def encodePostData(data):
	data = urllib.urlencode(data)
	return data

def source(url, close=True, error=False, proxy=None, post=None, headers=None, mobile=False, safe=False, referer=None, cookie=None, output='', timeout='30'):
	return request(url, close, error, proxy, post, headers, mobile, safe, referer, cookie, output, timeout)


def parseDOM(html, name=u"", attrs={}, ret=False):
	# Copyright (C) 2010-2011 Tobias Ussing And Henrik Mosgaard Jensen

	if isinstance(html, str):
		try:
			html = [html.decode("utf-8")] # Replace with chardet thingy
		except:
			html = [html]
	elif isinstance(html, unicode):
		html = [html]
	elif not isinstance(html, list):
		return u""

	if not name.strip():
		return u""

	ret_lst = []
	for item in html:
		temp_item = re.compile('(<[^>]*?\n[^>]*?>)').findall(item)
		for match in temp_item:
			item = item.replace(match, match.replace("\n", " "))

		lst = []
		for key in attrs:
			lst2 = re.compile('(<' + name + '[^>]*?(?:' + key + '=[\'"]' + attrs[key] + '[\'"].*?>))', re.M | re.S).findall(item)
			if len(lst2) == 0 and attrs[key].find(" ") == -1:  # Try matching without quotation marks
				lst2 = re.compile('(<' + name + '[^>]*?(?:' + key + '=' + attrs[key] + '.*?>))', re.M | re.S).findall(item)

			if len(lst) == 0:
				lst = lst2
				lst2 = []
			else:
				test = range(len(lst))
				test.reverse()
				for i in test:  # Delete anything missing from the next list.
					if not lst[i] in lst2:
						del(lst[i])

		if len(lst) == 0 and attrs == {}:
			lst = re.compile('(<' + name + '>)', re.M | re.S).findall(item)
			if len(lst) == 0:
				lst = re.compile('(<' + name + ' .*?>)', re.M | re.S).findall(item)

		if isinstance(ret, str):
			lst2 = []
			for match in lst:
				attr_lst = re.compile('<' + name + '.*?' + ret + '=([\'"].[^>]*?[\'"])>', re.M | re.S).findall(match)
				if len(attr_lst) == 0:
					attr_lst = re.compile('<' + name + '.*?' + ret + '=(.[^>]*?)>', re.M | re.S).findall(match)
				for tmp in attr_lst:
					cont_char = tmp[0]
					if cont_char in "'\"":
						# Limit down to next variable.
						if tmp.find('=' + cont_char, tmp.find(cont_char, 1)) > -1:
							tmp = tmp[:tmp.find('=' + cont_char, tmp.find(cont_char, 1))]

						# Limit to the last quotation mark
						if tmp.rfind(cont_char, 1) > -1:
							tmp = tmp[1:tmp.rfind(cont_char)]
					else:
						if tmp.find(" ") > 0:
							tmp = tmp[:tmp.find(" ")]
						elif tmp.find("/") > 0:
							tmp = tmp[:tmp.find("/")]
						elif tmp.find(">") > 0:
							tmp = tmp[:tmp.find(">")]

					lst2.append(tmp.strip())
			lst = lst2
		else:
			lst2 = []
			for match in lst:
				endstr = u"</" + name

				start = item.find(match)
				end = item.find(endstr, start)
				pos = item.find("<" + name, start + 1 )

				while pos < end and pos != -1:
					tend = item.find(endstr, end + len(endstr))
					if tend != -1:
						end = tend
					pos = item.find("<" + name, pos + 1)

				if start == -1 and end == -1:
					temp = u""
				elif start > -1 and end > -1:
					temp = item[start + len(match):end]
				elif end > -1:
					temp = item[:end]
				elif start > -1:
					temp = item[start + len(match):]

				if ret:
					endstr = item[end:item.find(">", item.find(endstr)) + 1]
					temp = match + temp + endstr

				item = item[item.find(temp, item.find(match)) + len(temp):]
				lst2.append(temp)
			lst = lst2
		ret_lst += lst

	return ret_lst


def replaceHTMLCodes(txt):
	txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
	txt = HTMLParser.HTMLParser().unescape(txt)
	txt = txt.replace("&quot;", "\"")
	txt = txt.replace("&amp;", "&")
	return txt

def cleanHTMLCodes(txt):
	txt = txt.replace("'", "")
	txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
	txt = HTMLParser.HTMLParser().unescape(txt)
	txt = txt.replace("&quot;", "\"")
	txt = txt.replace("&amp;", "&")

	return txt

def agent():
	return randomagent()

def randomagent():
	BR_VERS = [
		['%s.0' % i for i in xrange(18, 43)],
		['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111', '39.0.2171.71', '39.0.2171.95', '39.0.2171.99', '40.0.2214.93', '40.0.2214.111',
		 '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124', '44.0.2403.155', '44.0.2403.157', '45.0.2454.101', '45.0.2454.85', '46.0.2490.71',
		 '46.0.2490.80', '46.0.2490.86', '47.0.2526.73', '47.0.2526.80'],
		['11.0']]
	WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
	FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
	RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
				'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36']
	index = random.randrange(len(RAND_UAS))
	return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[index]))

def googletag(url):
	quality = re.compile('itag=(\d*)').findall(url)
	quality += re.compile('=m(\d*)$').findall(url)
	try: quality = quality[0]
	except: return []
	#control.log('<><><><><><><><><><><><> %s <><><><><><><><><>' % quality)
	if quality in ['37', '137', '299', '96', '248', '303', '46']:
		return [{'source': 'gvideo', 'quality': u'1080p', 'url': url}]
	elif quality in ['22', '84', '136', '298', '120', '95', '247', '302', '45', '102']:
		return [{'source': 'gvideo', 'quality': u'720p', 'url': url}]
	elif quality in ['35', '44', '135', '244', '94', '59']:
		return [{'source': 'gvideo', 'quality': u'480p', 'url': url}]
	elif quality in ['18', '34', '43', '82', '100', '101', '134', '243', '93']:
		return [{'source': 'gvideo', 'quality': u'480p', 'url': url}]
	elif quality in ['5', '6', '36', '83', '133', '242', '92', '132']:
		return [{'source': 'gvideo', 'quality': u'480p', 'url': url}]
	else:
		return [{'source': 'gvideo', 'quality': u'720p', 'url': url}]
		
def geturlhost(url):
	try:
		urlhost = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
	except:
		urlhost = None
	
	return urlhost

class cfcookie:
	def __init__(self):
		self.cookie = None


	def get(self, netloc, ua, timeout):
		threads = []

		for i in range(0, 3): threads.append(workers.Thread(self.get_cookie, netloc, ua, timeout))
		[i.start() for i in threads]

		for i in range(0, 15):
			if not self.cookie == None: return self.cookie
			time.sleep(1)


	def get_cookie(self, netloc, ua, timeout):
		try:
			headers = {'User-Agent': ua}

			request = urllib2.Request(netloc, headers=headers)

			try:
				response = urllib2.urlopen(request, timeout=int(timeout))
			except urllib2.HTTPError as response:
				result = response.read(5242880)

			jschl = re.findall('name="jschl_vc" value="(.+?)"/>', result)[0]

			init = re.findall('setTimeout\(function\(\){\s*.*?.*:(.*?)};', result)[-1]

			builder = re.findall(r"challenge-form\'\);\s*(.*)a.v", result)[0]

			decryptVal = self.parseJSString(init)

			lines = builder.split(';')

			for line in lines:

				if len(line) > 0 and '=' in line:

					sections=line.split('=')
					line_val = self.parseJSString(sections[1])
					decryptVal = int(eval(str(decryptVal)+sections[0][-1]+str(line_val)))

			answer = decryptVal + len(urlparse.urlparse(netloc).netloc)

			query = '%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (netloc, jschl, answer)

			if 'type="hidden" name="pass"' in result:
				passval = re.findall('name="pass" value="(.*?)"', result)[0]
				query = '%s/cdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (netloc, urllib.quote_plus(passval), jschl, answer)
				time.sleep(6)

			cookies = cookielib.LWPCookieJar()
			handlers = [urllib2.HTTPHandler(), urllib2.HTTPSHandler(), urllib2.HTTPCookieProcessor(cookies)]
			opener = urllib2.build_opener(*handlers)
			opener = urllib2.install_opener(opener)

			try:
				request = urllib2.Request(query, headers=headers)
				response = urllib2.urlopen(request, timeout=int(timeout))
			except:
				pass

			cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])

			if 'cf_clearance' in cookie: self.cookie = cookie
		except:
			pass


	def parseJSString(self, s):
		try:
			offset=1 if s[0]=='+' else 0
			val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
			return val
		except:
			pass

class sucuri:
	def __init__(self):
		self.cookie = None


	def get(self, result):
		try:
			s = re.compile("S\s*=\s*'([^']+)").findall(result)[0]
			s = base64.b64decode(s)
			s = s.replace(' ', '')
			s = re.sub('String\.fromCharCode\(([^)]+)\)', r'chr(\1)', s)
			s = re.sub('\.slice\((\d+),(\d+)\)', r'[\1:\2]', s)
			s = re.sub('\.charAt\(([^)]+)\)', r'[\1]', s)
			s = re.sub('\.substr\((\d+),(\d+)\)', r'[\1:\1+\2]', s)
			s = re.sub(';location.reload\(\);', '', s)
			s = re.sub(r'\n', '', s)
			s = re.sub(r'document\.cookie', 'cookie', s)

			cookie = '' ; exec(s)
			self.cookie = re.compile('([^=]+)=(.*)').findall(cookie)[0]
			self.cookie = '%s=%s' % (self.cookie[0], self.cookie[1])

			return self.cookie
		except:
			pass

def parseJSString(s):
	try:
		offset=1 if s[0]=='+' else 0
		val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
		return val
	except:
		pass

def googlepass(url):
	try:
		try: headers = dict(urlparse.parse_qsl(url.rsplit('|', 1)[1]))
		except: headers = None
		url = request(url.split('|')[0], headers=headers, output='geturl')
		if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
		else: url = url.replace('https://', 'http://')
		if headers: url += '|%s' % urllib.urlencode(headers)
		return url
	except:
		return
		
def getUrlHost(url):
	try:
		urlhost = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
	except:
		urlhost = url[0:10]
	return urlhost
		
def b64encode(ret):
	return base64.b64encode(ret)
	
def b64decode(ret):
	return base64.b64decode(ret)
	
def b64eencode(ret):
	return base64.b64encode(base64.b64encode(ret))
	
def b64ddecode(ret):
	return base64.b64decode(base64.b64decode(ret))

def search_regex(pattern, string, name, default=None, fatal=True, flags=0, group=None):
	mobj = re.search(pattern, string, flags)
	if mobj:
		if group is None:
		# return the first matching group
			#return next(g for g in mobj.groups() if g is not None) -- next function is Python 2.6+
			myIterator  = (g for g in mobj.groups() if g is not None)
			for nextval in myIterator:
				return nextval
		else:
			return mobj.group(group)
	else:
		return None
