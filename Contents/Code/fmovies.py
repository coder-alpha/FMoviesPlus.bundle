#
# Coder Alpha
# https://github.com/coder-alpha
#
# Adapted from lambda's Kodi plugin
# https://github.com/lambda81
# and modified for use with Plex Media Server
#
#########################################################################################################

import urllib, urllib2, urlparse, json, time, re, sys, HTMLParser, random, cookielib, datetime, calendar

Constants = SharedCodeService.constants

CACHE = {}
CACHE_EXPIRY_TIME = 60*60 # 1 Hour

GLOBAL_TIMEOUT_FOR_HTTP_REQUEST = 15
HTTP_GOOD_RESP_CODES = ['200','206']

BASE_URL = "https://www.fmovies.to"
HASH_PATH_MENU = "/user/ajax/menu-bar"
HASH_PATH_INFO = "/ajax/episode/info"
SEARCH_PATH = "/search"
FILTER_PATH = "/filter"
KEYWORD_PATH = "/tag/"
STAR_PATH = "/star/"

# SSL Web Proxy
PROXY_URL = "https://ssl-proxy.my-addr.org/myaddrproxy.php/"
PROXY_PART1 = "/myaddrproxy.php/https/fmovies.to/"
PROXY_PART1_REPLACE = "/"
PROXY_PART2A = "/myaddrproxy.php/https/"
PROXY_PART2B = "/myaddrproxy.php/http/"
PROXY_PART2_REPLACE = "//"

####################################################################################################

# Get FMovies-API
#@route(PREFIX + '/getapiurl')
def GetApiUrl(url, key, serverts=0):

	use_debug = Prefs["use_debug"]
	use_https_alt = Prefs["use_https_alt"]
	use_web_proxy = Prefs["use_web_proxy"]
	
	res = None
	myts = time.time()
	
	try:
		CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		CACHE_EXPIRY = CACHE_EXPIRY_TIME
	
	if key in CACHE and 'myts' in CACHE[key] and (myts - int(CACHE[key]['myts']) < CACHE_EXPIRY):
		if use_debug:
			Log("Using Movie Link from Cache")
		res = CACHE[key]['res']
		isOpenLoad = CACHE[key]['isOpenLoad']
		if isOpenLoad == 'True':
			isOpenLoad = True
		else:
			if res == 'Unavailable':
				res = None
			isOpenLoad = False
	else:
		if use_debug:
			Log("Retrieving Fresh Movie Link")
			
		ret, isOpenLoad = get_sources(url=url, key=key, use_debug=use_debug, serverts=serverts, myts=myts, use_https_alt=use_https_alt, webproxy=None if not use_web_proxy else PROXY_URL)
		if use_debug:
			Log("get_sources url: %s, key: %s" % (url,key))
			Log("get_sources ret: %s" % ret)
		
		if ret == None: # if the request ever fails - clear CACHE right away and make 2nd attempt
			CACHE.clear()
			if use_debug:
				Log("CACHE cleared due to null response from API - maybe cookie issue for %s" % url)
			ret, isOpenLoad = get_sources(url=url, key=key, use_debug=use_debug, serverts=serverts, myts=myts, use_https_alt=use_https_alt, webproxy=None if not use_web_proxy else PROXY_URL)
			
		if ret == None:
			if use_debug:
				Log("null response from API (possible file deleted) - for %s" % url)
		else:
			if isOpenLoad:
				res = ret
				CACHE[key] = {}
				CACHE[key]['res'] = res
				CACHE[key]['serverts'] = serverts
				CACHE[key]['myts'] = myts
				CACHE[key]['isOpenLoad'] = str(isOpenLoad)
				if use_debug:
					Log("Added " + key + " to CACHE")
			else:
				# fix api url to https
				ret = ret.replace('http://','https://')

				data = None
				if use_https_alt:
					try:
						vars = request(url=ret, output='response')
						if vars != None and len(vars) > 0 and vars[0] in HTTP_GOOD_RESP_CODES:
							data = json.loads(vars[1])
						else:
							Log('ERROR fmovies.py>GetApiUrl1: Url:%s returned Vars:%s' % (ret, vars))
					except Exception as e:
						Log('ERROR fmovies.py>GetApiUrl2: Args:%s, Url:%s returned %s' % (e.args,ret,vars))
						pass
				elif use_web_proxy:
					json_data_string = HTTP.Request(PROXY_URL + ret).content
					json_data_string = json_data_string.replace(PROXY_PART1, PROXY_PART1_REPLACE)
					json_data_string = json_data_string.replace(PROXY_PART2A, PROXY_PART2_REPLACE)
					json_data_string = json_data_string.replace(PROXY_PART2B, PROXY_PART2_REPLACE)
					try:
						data = JSON.ObjectFromString(json_data_string)
					except Exception as e:
						Log('ERROR fmovies.py>GetApiUrl3: Args:%s, Url:%s, StringData:%s' % (e.args,ret,json_data_string))
						pass
				else:
					try:
						data = JSON.ObjectFromURL(ret)
					except Exception as e:
						Log('ERROR fmovies.py>GetApiUrl4: Args:%s, Url:%s' % (e.args,ret))
						pass
					
				if data == None:
					return None, isOpenLoad
				if data['error'] == None:
					res = JSON.StringFromObject(data['data'])
					CACHE[key] = {}
					CACHE[key]['res'] = res
					CACHE[key]['serverts'] = serverts
					CACHE[key]['myts'] = myts
					CACHE[key]['isOpenLoad'] = str(isOpenLoad)
					if use_debug:
						Log("Added " + key + " to CACHE")

	return res, isOpenLoad

def get_sources(url, key, use_debug=True, serverts=0, myts=0, use_https_alt=False, webproxy=None):

	if serverts == 0:
		#serverts = ((int(time.time())/3600)*3600)
		# 1485273600
		# 1485324000
		# 1485327600
		# 1485324000
		# 1485352800
		utc = datetime.datetime.utcnow()
		if utc.hour < 6:
			past = utc - datetime.timedelta(hours=13) 	# 1485273600
		elif utc.hour >= 6 and utc.hour < 16:
			past = utc									# 1485324000, 1485327600, 1485352800
		else:
			past = utc - datetime.timedelta(hours=12)	# 1485324000, 1485334800
		
		past_fixed = datetime.datetime(past.year, past.month, past.day, past.hour, 0, 0, 0)
		serverts = calendar.timegm(past_fixed.timetuple())
	
	try:
		magic_url = None
		isOpenLoad = False
		if url == None: return magic_url
		referer = url
		
		try:
			CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
		except:
			CACHE_EXPIRY = CACHE_EXPIRY_TIME
		
		if 'cookie' in CACHE and 'myts' in CACHE['cookie'] and (myts - int(CACHE['cookie']['myts'])) < CACHE_EXPIRY:
			# use cache to minimize requests
			if use_debug:
				try:
					Log('Using Cookies from Cache')
				except:
					print 'Using Cookies from Cache'
			cookie1 = CACHE['cookie']['cookie1']
			cookie2 = CACHE['cookie']['cookie2']
		else:
			if use_debug:
				try:
					Log('NOT Using Cookies from Cache')
				except:
					print 'NOT Using Cookies from Cache'
			CACHE['cookie'] = {}
			serverts = str(serverts)
			time.sleep(0.2)
			result, headers, content, cookie1 = request(url, limit='0', output='extended', httpsskip=use_https_alt, webproxy=webproxy)
			#print result
			CACHE['cookie']['cookie1'] = cookie1
			hash_url = urlparse.urljoin(BASE_URL, HASH_PATH_MENU)
			query = {'ts': serverts}
			query.update(get_token(query))
			hash_url = hash_url + '?' + urllib.urlencode(query)
			time.sleep(0.2)
			r1, headers, content, cookie2 = request(hash_url, limit='0', output='extended', cookie=cookie1, httpsskip=use_https_alt, webproxy=webproxy)
			#print r1
			CACHE['cookie']['cookie2'] = cookie2
			CACHE['cookie']['myts'] = myts

		try:
			headers = {'X-Requested-With': 'XMLHttpRequest'}
			hash_url = urlparse.urljoin(BASE_URL, HASH_PATH_INFO)
			query = {'ts': serverts, 'id': key}

			query.update(get_token(query))
			hash_url = hash_url + '?' + urllib.urlencode(query)

			headers['Referer'] = urlparse.urljoin(url, key)
			oldmarketgidstorage = 'MarketGidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A3%2C%22TejndEEDj%22%3A%22MTQ4MTM2ODE0NzM0NzQ4NTMyOTAx%22%7D%2C%22C48532%22%3A%7B%22page%22%3A1%2C%22time%22%3A1481368147359%7D%2C%22C77945%22%3A%7B%22page%22%3A1%2C%22time%22%3A1481368147998%7D%2C%22C77947%22%3A%7B%22page%22%3A1%2C%22time%22%3A1481368148109%7D%7D'
			newmarketgidstorage = 'MarketGidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A75%2C%22TejndEEDj%22%3A%22MTQ4NDc3MzczNzkzOTc3OTQ0NjgwMQ%3D%3D%22%7D%2C%22C77944%22%3A%7B%22page%22%3A1%2C%22time%22%3A1485149595898%7D%2C%22C77946%22%3A%7B%22page%22%3A1%2C%22time%22%3A1485149600480%7D%2C%22C77948%22%3A%7B%22page%22%3A1%2C%22time%22%3A1485149600326%7D%7D'
			headers['Cookie'] = cookie1 + ';' + cookie2 + ';user-info=null; ' + newmarketgidstorage
			
			time.sleep(0.4)
			#print hash_url
			result = request(hash_url, headers=headers, limit='0', webproxy=webproxy)
			if webproxy != None:
				result = result.replace(PROXY_PART1, PROXY_PART1_REPLACE)
				result = result.replace(PROXY_PART2A, PROXY_PART2_REPLACE)
				result = result.replace(PROXY_PART2B, PROXY_PART2_REPLACE)
			#print result
			
			result = json.loads(result)

			if 'error' in result:
				grabber = None
			elif result['target'] != "":
				grabber = result['target']
				isOpenLoad = True
			else:
				query = {'id': key}
				query.update(get_token(query))
				url = url + '?' + urllib.urlencode(query)
				query = {'id':result['params']['id']}
				query.update(get_token(query))
				query = {'id':result['params']['id'], 'token':result['params']['token']}
				grabber = result['grabber'] + '?' + urllib.urlencode(query)
			if not grabber.startswith('http'):
				grabber = 'http:'+grabber
				
			magic_url = grabber	
		except:
			pass

		return magic_url, isOpenLoad
	except:
		return magic_url, isOpenLoad

def get_token(data):

	index1 = 0
	sn = 256
	for index2 in data:
		i = list(range(0, sn))
		if not index2.startswith('_'):
			n = 0
			index4 = 0
			for s in range(0, sn):
				n = (n + i[s] +
					 ord(index2[s % len(index2)])) % sn
				r = i[s]
				i[s] = i[n]
				i[n] = r
			n = 0
			for index8 in range(0, len(data[index2])):
				s = index8 + 1  # line:15
				n = (n + i[s]) % (sn)
				r = i[s]
				i[s] = i[n]
				i[n] = r
				index4 += ord(data[index2][index8]) ^ (i[(i[s] +i[n]) % sn]) * index8 + index8
			index1 += index4
	return {'_': str(index1)}

	
#########################################################################################################
def request(url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, webproxy=None, use_web_proxy=False):
	try:

		handlers = []
		redirectURL = url
		
		if webproxy != None:
			url = webproxy + url
		elif use_web_proxy:
			url = PROXY_URL + url

		if not proxy == None:
			handlers += [urllib2.ProxyHandler({'http':'%s' % (proxy)}), urllib2.HTTPHandler]
			opener = urllib2.build_opener(*handlers)
			opener = urllib2.install_opener(opener)

		if output == 'cookie2' or output == 'cookie' or output == 'extended' or not close == True:
			cookies = cookielib.LWPCookieJar()
			if httpsskip or webproxy != None or use_web_proxy:
				handlers += [urllib2.HTTPHandler(), urllib2.HTTPCookieProcessor(cookies)]
			else:
				handlers += [urllib2.HTTPHandler(), urllib2.HTTPSHandler(), urllib2.HTTPCookieProcessor(cookies)]
			opener = urllib2.build_opener(*handlers)
			opener = urllib2.install_opener(opener)
			
		try:
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
			headers['Referer'] = '%s://%s/' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)
		else:
			headers['Referer'] = referer
		if not 'Accept-Language' in headers:
			headers['Accept-Language'] = 'en-US'
		if 'Cookie' in headers:
			pass
		elif not cookie == None:
			headers['Cookie'] = cookie

		if redirect == False:
			class NoRedirection(urllib2.HTTPErrorProcessor):
				def http_response(self, request, response): return response

			opener = urllib2.build_opener(NoRedirection)
			opener = urllib2.install_opener(opener)

			try: del headers['Referer']
			except: pass
			
		redirectHandler = None
		urlList = []
		if followredirect:
			class HTTPRedirectHandler(urllib2.HTTPRedirectHandler):
				def redirect_request(self, req, fp, code, msg, headers, newurl):
					newreq = urllib2.HTTPRedirectHandler.redirect_request(self,
						req, fp, code, msg, headers, newurl)
					if newreq is not None:
						self.redirections.append(newreq.get_full_url())
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
			#Log("AAAA- CODE %s|%s " % (url, response.code))
			if response.code == 503:
				#Log("AAAA- CODE %s|%s " % (url, response.code))
				if 'cf-browser-verification' in response.read(5242880):
					#Log("CF-OK")

					netloc = '%s://%s' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)
					#cf = cache.get(cfcookie, 168, netloc, headers['User-Agent'], timeout)
					cf = cfcookie(netloc, headers['User-Agent'], timeout)
					
					headers['Cookie'] = cf
					request = urllib2.Request(url, data=post, headers=headers)
					response = urllib2.urlopen(request, timeout=int(timeout))
				elif error == False:
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

			elif error == False:
				print ("Response code",response.code, response.msg,url)
				return

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
			if content < (2048 * 1024):return
			result = response.read(16 * 1024)
			if close == True: response.close()
			return result

		elif output == 'extended':
			try: cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
			except: pass
			try: cookie = cf
			except: pass
			content = response.headers
			result = response.read(5242880)
			return (result, headers, content, cookie)

		elif output == 'geturl':
			result = response.geturl()

		elif output == 'headers':
			content = response.headers
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

		return result
	except Exception as e:
		Log('ERROR fmovies.py>request %s, %s' % (e.args,url))
		return
	
#########################################################################################################
#
# eval is not supported in PMS ver. of Python
#
def cfcookie(netloc, ua, timeout):
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

		decryptVal = parseJSString(init)

		lines = builder.split(';')

		for line in lines:

			if len(line) > 0 and '=' in line:

				sections=line.split('=')
				line_val = parseJSString(sections[1])
				decryptVal = int(eval(str(decryptVal)+sections[0][-1]+str(line_val))) #<--------------------- eval is not supported in PMS ver. of Python

		answer = decryptVal + len(urlparse.urlparse(netloc).netloc)

		query = '%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (netloc, jschl, answer)

		if 'type="hidden" name="pass"' in result:
			passval = re.findall('name="pass" value="(.*?)"', result)[0]
			query = '%s/cdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (netloc, urllib.quote_plus(passval), jschl, answer)
			time.sleep(5)

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

		return cookie
	except Exception as e:
		Log('ERROR fmovies.py>cfcookie: %s' % (e.args))
		return
		
def parseJSString(s):
	try:
		offset=1 if s[0]=='+' else 0
		val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:])) #<--------------------- eval is not supported in PMS ver. of Python
		return val
	except:
		pass
		
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
				'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
				'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko']
	index = random.randrange(len(RAND_UAS))
	return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[index]))
	
def replaceHTMLCodes(txt):
	txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
	txt = HTMLParser.HTMLParser().unescape(txt)
	txt = txt.replace("&quot;", "\"")
	txt = txt.replace("&amp;", "&")
	return txt
	
#########################################################################################################
