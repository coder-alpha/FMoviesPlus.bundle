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


import re,urllib,urlparse,pkgutil,json,time

from resources.lib.libraries import client
from resources.lib.libraries import control
	
sourceHosts = []
sourceHostsCall = []
sourceHostsPlaybackSupport = {}

def init():
	del sourceHosts[:]
	del sourceHostsCall[:]
	sourceHostsPlaybackSupport.clear()
	
	for package, name, is_pkg in pkgutil.walk_packages(__path__):	
		try:
			c = __import__(name, globals(), locals(), [], -1).host()
			log("Adding Host %s to Interface" % (c.info()['name']))
			sourceHostsCall.append({'host': c.info()['host'], 'name': c.info()['name'], 'call': c})
			sourceHosts.append((c.info()))
			sourceHostsPlaybackSupport[c.info()['name']] = c.info()['playbacksupport']
		except Exception as e:
			log(type='CRITICAL', err='Could not import %s > %s (Retrying)' % (name,e))
			try:
				c = __import__(name, globals(), locals(), [], -1).host()
				log("Adding Host %s to Interface" % (c.info()['name']))
				sourceHostsCall.append({'host': c.info()['host'], 'name': c.info()['name'], 'call': c})
				sourceHosts.append((c.info()))
				sourceHostsPlaybackSupport[c.info()['name']] = c.info()['playbacksupport']
			except Exception as e:
				log(type='CRITICAL', err='Could not import %s > %s (Retry-Failed)' % (name,e))
				error_info = {
					'name': name,
					'ver': '0.0.0',
					'date': 'Jan. 01, 2000',
					'class': name,
					'speed': 0,
					'netloc': name,
					'host': name,
					'quality': 'N/A',
					'logo': None,
					'working': False,
					'resolver': False,
					'captcha': False,
					'msg': e,
					'playbacksupport': False,
					'a/c': False,
					'streaming' : False,
					'downloading' : False
				}
				sourceHostsCall.append({'host': error_info['host'], 'name': error_info['name'], 'call': None})
				sourceHosts.append(error_info)
				sourceHostsPlaybackSupport[error_info['name']] = error_info['playbacksupport']


def request(url):
	try:
		if '</regex>' in url:
			import regex ; url = regex.resolve(url)
	except:
		pass
	
	try:
		urlhost = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
		for host in sourceHostsCall:
			if urlhost in host['host']:
				ret = host['call'].resolve(url)
				log("#RESOLVER FOUND# url : %s -- %s" % (url, host['name']))
				return ret
	except:
		pass

	return None	
		
def resolve(url):
	try:
		ret = url
		urlhost = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
		for host in sourceHostsCall:
			if urlhost in host['host']:
				ret = host['call'].resolve(url)
				break
		return ret
	except:
		return url
		
def resolveHostname(h):
	try:
		ret = h
		for host in sourceHostsCall:
			if h in host['host']:
				ret = host['call'].resolveHostname(h)
				break
		return ret
	except:
		return h
		
def testLink(url):
	try:
		urlhost = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
		for host in sourceHostsCall:
			if urlhost in host['host']:
				return host['call'].testLink(url)
		return 'Unknown'
	except:
		return 'Unknown'
		
def createMeta(url, provider, logo, quality, links, key, riptype=None, vidtype='Movie', lang='en', sub_url=None, txt='', file_ext='.mp4', testing=False):

	if url == None or url == '':
		return links
		
	url = url.strip()
	
	
	for item in links:
		if url == item['durl']:
			log("%s has already been processed" % url)
			return links
	
	quality = fixquality(quality)
	links_m=[]
	urldata = client.b64encode(json.dumps('', encoding='utf-8'))
	params = client.b64encode(json.dumps('', encoding='utf-8'))
	
	try:
		try:
			urlhost = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
		except:
			urlhost = re.findall('([\w]+[.][\w]+).*$', urlparse.urlparse(url.strip().lower()).netloc)[0]
			urlhost = urlhost.split('.')[1]
			
		if riptype == None:
			riptype_def = 'BRRIP'
		else:
			riptype_def = riptype
		for host in sourceHostsCall:
			log("Searching %s in %s" % (urlhost, host['host']), logToControl=False)

			if urlhost in host['host']:
				log("Found %s in %s" % (urlhost, host['host']))
				return host['call'].createMeta(url, provider, logo, quality, links, key, riptype_def, vidtype=vidtype, lang=lang, sub_url=sub_url, txt=txt, file_ext=file_ext, testing=testing)
				
		log("urlhost '%s' not found in host/resolver plugins - creating generic meta for external services" % urlhost)
				
		quality = file_quality(url, quality)
		
		if riptype == None:
			type = rip_type(url, quality)
		else:
			type = riptype
		
		links_m.append({'source':urlhost, 'maininfo':'', 'titleinfo':'', 'quality':quality, 'vidtype':vidtype, 'rip':type, 'provider':provider, 'url':url, 'durl':url, 'urldata':urldata, 'params':params, 'logo':logo, 'online':'Unknown', 'allowsDownload':False, 'resumeDownload':False, 'allowsStreaming':True, 'key':key, 'enabled':True, 'fs':int(0), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'subdomain':client.geturlhost(url), 'misc':{'player':'eplayer', 'gp':False}})
	except Exception as e:
		log(type='ERROR', err="createMeta : %s url: %s" % (e.args, url))
		
	links += [l for l in links_m]
	return links

def fixquality(quality):
	if quality == '1080p':
		quality = '1080p'
	elif (quality == 'HD' or quality == 'HQ' or '720' in quality):
		quality = '720p'
	elif quality == 'SD' or '480' in quality:
		quality = '480p'
	elif quality == 'CAM' or quality == 'SCR':
		quality = quality
	else:
		quality = '360p'

	return quality

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
		
		return unicode(type.upper())
	except:
		return unicode(type.upper())
		
def check(url):
	http_res = client.request(url=url, output='responsecode')
	if http_res not in client.HTTP_GOOD_RESP_CODES:
		return False
	return True

def hostsplaybacksupport():

	return sourceHostsPlaybackSupport
	
def info():
	
	return sourceHosts
	
def log(err='', type='INFO', logToControl=True, doPrint=True):
	try:
		msg = '%s: %s > %s : %s' % (time.ctime(time.time()), type, 'resolvers', err)
		if logToControl == True:
			control.log(msg)
		if control.doPrint == True and doPrint == True:
			print msg
	except Exception as e:
		control.log('Error in Logging: %s >>> %s' % (msg,e))
