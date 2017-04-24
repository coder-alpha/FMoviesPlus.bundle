import time, fmovies, base64, unicodedata, re

################################################################################
TITLE = "FMoviesPlus"
VERSION = '0.16' # Release notation (x.y - where x is major and y is minor)
GITHUB_REPOSITORY = 'coder-alpha/FMoviesPlus.bundle'
PREFIX = "/video/fmoviesplus"
################################################################################


# Vibrant Emoji's (might not be supported on all clients)
EMOJI_LINK = u'\U0001F517'
EMOJI_GREEN_HEART = u'\U0001F49A'
EMOJI_BROKEN_HEART = u'\U0001F494'

# Simple Emoji's
EMOJI_HEART = u'\u2665'
EMOJI_TICK = u'\u2713'
EMOJI_CROSS = u'\u2717'
EMOJI_QUESTION = u'\u2753'


####################################################################################################
# Get Key from a Dict using Val
@route(PREFIX + '/GetEmoji')
def GetEmoji(type, mode='vibrant'):

	# modes = ['simple','vibrant'] - enforce mode to override Prefs for Search Filter

	if mode == 'simple' or Prefs["use_vibrant_emoji"] == False:
		if type == 'pos' or type == 'true':
			return EMOJI_TICK
		elif type =='neg' or type == 'false':
			return EMOJI_CROSS
	else:
		if type == 'pos' or type == 'true':
			return EMOJI_GREEN_HEART
		elif type =='neg' or type == 'false':
			return EMOJI_BROKEN_HEART
	
	return EMOJI_QUESTION


####################################################################################################
# Get Key from a Dict using Val
@route(PREFIX + '/getkeyfromval')
def GetKeyFromVal(list, val_look):
	for key, val in list.iteritems():
		if val == val_look:
			return key
			
####################################################################################################
# Gets a client specific identifier
@route(PREFIX + '/getsession')
def getSession():

	session = 'UnknownPlexClientSession'
	if 'X-Plex-Client-Identifier' in str(Request.Headers):
		session = str(Request.Headers['X-Plex-Client-Identifier'])
	elif 'X-Plex-Target-Client-Identifier' in str(Request.Headers):
		session = str(Request.Headers['X-Plex-Target-Client-Identifier'])
	elif 'User-Agent' in str(Request.Headers) and 'X-Plex-Token' in str(Request.Headers):
		session = 'UnknownClient-'+encode(str(Request.Headers['User-Agent']) + str(Request.Headers['X-Plex-Token'][:3]))[:10]
	
	return (session)

#######################################################################################################
# base64 decode
@route(PREFIX + '/decode')
def decode(str):

	return base64.b64decode(str)
	
# base64 encode
@route(PREFIX + '/encode')
def encode(str):

	return base64.b64encode(str)

#######################################################################################################
@route(PREFIX + "/setDictVal")
def setDictVal(key, session, val):
	Dict[key+session] = val
	Dict.Save()
	if Prefs["use_debug"]:
		Log("%s status: %s" % (key,val))
		
	return ObjectContainer(header=key, message=key.replace('Toggle','') + ' has been ' + Dict[key+session] + ' for this device.', title1=key)

@route(PREFIX + "/UsingOption")
def UsingOption(key):
	session = getSession()
	if Dict[key+session] == None or Dict[key+session] == 'disabled':
		return False
	else:
		return True

####################################################################################################
# Get HTTP response code (200 == good)
@route(PREFIX + '/gethttpstatus')
def GetHttpStatus(url):
	try:
		req = GetHttpRequest(url=url)
		if req != None:
			conn = urllib2.urlopen(req, timeout=fmovies.GLOBAL_TIMEOUT_FOR_HTTP_REQUEST)
			resp = str(conn.getcode())
		else:
			resp = '0'
	except Exception as e:
		resp = '0'
	return resp
	
####################################################################################################
# Get HTTP request
@route(PREFIX + '/gethttprequest')
def GetHttpRequest(url, cookies=None):
	try:
		headers = {'User-Agent': fmovies.USER_AGENT,
		   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
		   'Accept-Encoding': 'none',
		   'Accept-Language': 'en-US,en;q=0.8',
		   'Connection': 'keep-alive',
		   'Referer': url}
		   
		if cookies != None:
			headers['Cookie'] = cookies
		if '|' in url:
			url_split = url.split('|')
			url = url_split[0]
			headers['Referer'] = url
			
			for params in url_split:
				if '=' in params:
					param_split = params.split('=')
					param = param_split[0].strip()
					param_val = urllib2.quote(param_split[1].strip(), safe='/=&')
					headers[param] = param_val

		if 'http://' in url or 'https://' in url:
			req = urllib2.Request(url, headers=headers)
		else:
			req = None
	except Exception as e:
		req = None
	return req
	
######################################################################################
@route(PREFIX + "/GetPageElements")
def GetPageElements(url, headers=None):

	page_data_elems = None
	try:
		page_data_string = GetPageAsString(url=url, headers=headers)
		page_data_elems = HTML.ElementFromString(page_data_string)
	except:
		pass
		
	return page_data_elems
	
######################################################################################
@route(PREFIX + "/GetPageAsString")
def GetPageAsString(url, headers=None, timeout=15):

	page_data_string = None
	try:
		if Prefs["use_https_alt"]:
			if Prefs["use_debug"]:
				Log("Using SSL Alternate Option")
				Log("Url: " + url)
			page_data_string = fmovies.request(url = url, headers=headers, timeout=str(timeout))
		elif Prefs["use_web_proxy"]:
			if Prefs["use_debug"]:
				Log("Using SSL Web-Proxy Option")
				Log("Url: " + url)
				
			if headers == None:
				page_data_string = HTTP.Request(fmovies.PROXY_URL + url, timeout=timeout).content
			else:
				page_data_string = HTTP.Request(fmovies.PROXY_URL + url, headers=headers, timeout=timeout).content
			page_data_string = page_data_string.replace(fmovies.PROXY_PART1, fmovies.PROXY_PART1_REPLACE)
			page_data_string = page_data_string.replace(fmovies.PROXY_PART1B, fmovies.PROXY_PART1_REPLACE)
			page_data_string = page_data_string.replace(fmovies.PROXY_PART1C, fmovies.PROXY_PART1_REPLACE)
			page_data_string = page_data_string.replace(fmovies.PROXY_PART2A, fmovies.PROXY_PART2_REPLACE)
			page_data_string = page_data_string.replace(fmovies.PROXY_PART2B, fmovies.PROXY_PART2_REPLACE)
		else:
			if headers == None:
				page_data_string = HTTP.Request(url, timeout=timeout).content
			else:
				page_data_string = HTTP.Request(url, headers=headers, timeout=timeout).content
	except Exception as e:
		Log('ERROR common.py>GetPageAsString: %s URL: %s' % (e,url))
		pass
		
	return page_data_string
		
####################################################################################################
@route(PREFIX + "/removeAccents")
def removeAccents(text):
	"""
	Convert input text to id.

	:param text: The input string.
	:type text: String.

	:returns: The processed String.
	:rtype: String.
	"""
	text = strip_accents(text.lower())
	text = re.sub('[ ]+', '_', text)
	text = re.sub('[^0-9a-zA-Z]', ' ', text)
	text = text.title()
	return text

def strip_accents(text):
	"""
	Strip accents from input String.

	:param text: The input string.
	:type text: String.

	:returns: The processed String.
	:rtype: String.
	"""
	try:
		text = unicode(text, 'utf-8')
	except NameError: # unicode is a default on python 3 
		pass
	text = unicodedata.normalize('NFD', text)
	text = text.encode('ascii', 'ignore')
	text = text.decode("utf-8")
	return str(text)


####################################################################################################
# author: Twoure
# source: https://github.com/Twoure/HindiMoviesOnline.bundle/blob/master/Contents/Code/messages.py
#
class NewMessageContainer(object):
	def __init__(self, prefix, title):
		self.title = title
		Route.Connect(prefix + '/message', self.message_container)

	def message_container(self, header, message):
		"""Setup MessageContainer depending on Platform"""

		if Client.Platform in ['Plex Home Theater', 'OpenPHT']:
			oc = ObjectContainer(
				title1=self.title, title2=header, no_cache=True,
				no_history=True, replace_parent=True
				)
			oc.add(PopupDirectoryObject(title=header, summary=message))
			return oc
		else:
			return MessageContainer(header, message)