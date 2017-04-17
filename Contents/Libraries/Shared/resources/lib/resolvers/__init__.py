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

def init():
	del sourceHosts[:]
	del sourceHostsCall[:]
	
	for package, name, is_pkg in pkgutil.walk_packages(__path__):	
		try:
			c = __import__(name, globals(), locals(), [], -1).host()
			print "Adding Host %s to Interface" % (c.info()['name'])
			sourceHostsCall.append({'host': c.info()['host'], 'name': c.info()['name'], 'call': c})
			sourceHosts.append((c.info()))
		except Exception as e:
			print "Error: %s - %s" % (name, e)	
			pass

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
				control.log("#RESOLVER FOUND# url : %s -- %s" % (url, host['name']))
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
		
def createMeta(url, provider, logo, quality, links, key):

	if url == None or url == '':
		print "resolvers > __init__.py > createMeta : url:%s prov:%s" % (url, provider)
		return links
		
	url = url.strip()
	
	quality = fixquality(quality)
	links_m=[]
	urldata = client.b64encode(json.dumps('', encoding='utf-8'))
	params = client.b64encode(json.dumps('', encoding='utf-8'))
	
	try:
		urlhost = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
		for host in sourceHostsCall:
			print "Searching %s in %s" % (urlhost, host['host'])
			if urlhost in host['host']:
				print "Found %s in %s" % (urlhost, host['host'])
				return host['call'].createMeta(url, provider, logo, quality, links, key)

				
		print "urlhost '%s' not found in host/resolver plugins" % urlhost
				
		quality = file_quality(url, quality)
		type = rip_type(url, quality)
		links_m.append({'source':urlhost, 'maininfo':'', 'titleinfo':'', 'quality':quality, 'rip':type, 'provider':provider, 'url':url, 'urldata':urldata, 'params':params, 'logo':logo, 'online':'Unknown', 'key':key, 'enabled':True, 'ts':time.time()})
	except Exception as e:
		print "ERROR resolvers > __init__.py > createMeta : %s url: %s" % (e.args, url)
		#quality = file_quality(url, quality)
		#type = rip_type(url, quality)
		#links_m.append({'source':urlhost, 'maininfo':'', 'titleinfo':'', 'quality':quality, 'rip':type, 'provider':provider, 'url':url, 'urldata':urldata, 'params':params, 'logo':logo, 'online':'Unknown', 'key':key, 'enabled':True})
		
	links += [l for l in links_m]
	return links

def fixquality(quality):
	if quality == '1080p':
		quality = '1080p'
	elif (quality == 'HD' or quality == 'HQ'):
		quality = '720p'
	elif quality == 'SD':
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

def info():
	
	return sourceHosts
	
	# return [{
		# 'class': '',
		# 'netloc': ['oboom.com', 'rapidgator.net', 'uploaded.net'],
		# 'host': ['Oboom', 'Rapidgator', 'Uploaded'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': True
	# }, {
		# 'class': 'okru',
		# 'netloc': ['ok.ru']
	# }, {
		# 'class': '',
		# 'netloc': ['youwatch.com','www.flashx.tv', 'thevideobee.to','auroravid.to', 'vshare.eu','shared.sx'],
		# 'host': ['youwatch', 'flashx', 'thevideobee','auroravid','vshare', 'shared'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': '_180upload',
		# 'netloc': ['180upload.com'],
		# 'host': ['180upload'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'allmyvideos',
		# 'netloc': ['allmyvideos.net', 'nosvideo.com','www.divxstage.to','noslocker.com'],
		# 'host': ['Allmyvideos','nosvideo', 'divxstage','noslocker'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'allvid',
		# 'netloc': ['allvid.ch'],
		# 'host': ['Allvid'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'bestreams',
		# 'netloc': ['bestreams.net'],
		# 'host': ['Bestreams'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'clicknupload',
		# 'netloc': ['clicknupload.com', 'clicknupload.link'],
		# 'host': ['Clicknupload'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'cloudtime',
		# 'netloc': ['cloudtime.to'],
		# 'host': ['Cloudtime'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'cloudyvideos',
		# 'netloc': ['cloudyvideos.com'],
		# #'host': ['Cloudyvideos'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'cloudzilla',
		# 'netloc': ['cloudzilla.to'],
		# 'host': ['Cloudzilla'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'daclips',
		# 'netloc': ['daclips.in'],
		# 'host': ['Daclips'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'yadisk',
		# 'netloc': ['yadi.sk']
	# }, {
		# 'class': 'dailymotion',
		# 'netloc': ['dailymotion.com']
	# }, {
		# 'class': 'datemule',
		# 'netloc': ['datemule.com']
	# }, {
		# 'class': 'divxpress',
		# 'netloc': ['divxpress.com'],
		# 'host': ['Divxpress'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'exashare',
		# 'netloc': ['exashare.com'],
		# 'host': ['Exashare'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'fastvideo',
		# 'netloc': ['fastvideo.in', 'faststream.in', 'rapidvideo.ws'],
		# 'host': ['Fastvideo', 'Faststream'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'filehoot',
		# 'netloc': ['filehoot.com'],
		# 'host': ['Filehoot'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'filenuke',
		# 'netloc': ['filenuke.com', 'sharesix.com'],
		# 'host': ['Filenuke', 'Sharesix'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'filmon',
		# 'netloc': ['filmon.com']
	# }, {
		# 'class': 'filepup',
		# 'netloc': ['filepup.net']
	# }, {
		# 'class': 'googledocs',
		# 'netloc': ['google.com']
	# }, {
		# 'class': 'googledocs',
		# 'netloc': ['docs.google.com', 'drive.google.com']
	# }, {
		# 'class': 'googlephotos',
		# 'netloc': ['photos.google.com']
	# }, {
		# 'class': 'googlepicasa',
		# 'netloc': ['picasaweb.google.com']
	# }, {
		# 'class': 'googleplus',
		# 'netloc': ['plus.google.com']
	# }, {
		# 'class': 'gorillavid',
		# 'netloc': ['gorillavid.com', 'gorillavid.in'],
		# 'host': ['Gorillavid'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'grifthost',
		# 'netloc': ['grifthost.com'],
		# #'host': ['Grifthost'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'hdcast',
		# 'netloc': ['hdcast.me']
	# }, {
		# 'class': 'hugefiles',
		# 'netloc': ['hugefiles.net'],
		# 'host': ['Hugefiles'],
		# 'quality': 'High',
		# 'captcha': True,
		# 'a/c': False
	# }, {
		# 'class': 'ipithos',
		# 'netloc': ['ipithos.to'],
		# 'host': ['Ipithos'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'ishared',
		# 'netloc': ['ishared.eu'],
		# 'host': ['iShared'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'kingfiles',
		# 'netloc': ['kingfiles.net'],
		# 'host': ['Kingfiles'],
		# 'quality': 'High',
		# 'captcha': True,
		# 'a/c': False
	# }, {
		# 'class': 'letwatch',
		# 'netloc': ['letwatch.us'],
		# 'host': ['Letwatch'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'mailru',
		# 'netloc': ['mail.ru', 'my.mail.ru', 'videoapi.my.mail.ru', 'api.video.mail.ru']
	# }, {
		# 'class': 'cloudmailru',
		# 'netloc': ['cloud.mail.ru']
	# }, {
		# 'class': 'mightyupload',
		# 'netloc': ['mightyupload.com'],
		# 'host': ['Mightyupload'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'movdivx',
		# 'netloc': ['movdivx.com'],
		# 'host': ['Movdivx'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'movpod',
		# 'netloc': ['movpod.net', 'movpod.in'],
		# 'host': ['Movpod'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'movshare',
		# 'netloc': ['movshare.net'],
		# 'host': ['Movshare'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'mrfile',
		# 'netloc': ['mrfile.me'],
		# 'host': ['Mrfile'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'mybeststream',
		# 'netloc': ['mybeststream.xyz']
	# }, {
		# 'class': 'nosvideo',
		# 'netloc': ['nosvideo.com'],
		# #'host': ['Nosvideo'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'novamov',
		# 'netloc': ['novamov.com'],
		# 'host': ['Novamov'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'nowvideo',
		# 'netloc': ['nowvideo.eu', 'nowvideo.sx'],
		# 'host': ['Nowvideo'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'openload',
		# 'netloc': ['openload.io', 'openload.co'],
		# 'host': ['Openload'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'p2pcast',
		# 'netloc': ['p2pcast.tv']
	# }, {
		# 'class': 'primeshare',
		# 'netloc': ['primeshare.tv'],
		# 'host': ['Primeshare'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'promptfile',
		# 'netloc': ['promptfile.com'],
		# 'host': ['Promptfile'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'putstream',
		# 'netloc': ['putstream.com'],
		# 'host': ['Putstream'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'realvid',
		# 'netloc': ['realvid.net'],
		# 'host': ['Realvid'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'sawlive',
		# 'netloc': ['sawlive.tv']
	# }, {
		# 'class': 'sharerepo',
		# 'netloc': ['sharerepo.com'],
		# 'host': ['Sharerepo'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'skyvids',
		# 'netloc': ['skyvids.net'],
		# 'host': ['Skyvids'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'speedvideo',
		# 'netloc': ['speedvideo.net']
	# }, {
		# 'class': 'stagevu',
		# 'netloc': ['stagevu.com'],
		# 'host': ['StageVu'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'streamcloud',
		# 'netloc': ['streamcloud.eu'],
		# 'host': ['Streamcloud'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'streamin',
		# 'netloc': ['streamin.to'],
		# 'host': ['Streamin'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'thefile',
		# 'netloc': ['thefile.me'],
		# 'host': ['Thefile'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'thevideo',
		# 'netloc': ['thevideo.me'],
		# 'host': ['Thevideo'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'turbovideos',
		# 'netloc': ['turbovideos.net'],
		# 'host': ['Turbovideos'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'tusfiles',
		# 'netloc': ['tusfiles.net'],
		# 'host': ['Tusfiles'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'up2stream',
		# 'netloc': ['up2stream.com'],
		# 'host': ['Up2stream'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'uploadc',
		# 'netloc': ['uploadc.com', 'uploadc.ch', 'zalaa.com'],
		# 'host': ['Uploadc', 'Zalaa'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'uploadrocket',
		# 'netloc': ['uploadrocket.net'],
		# 'host': ['Uploadrocket'],
		# 'quality': 'High',
		# 'captcha': True,
		# 'a/c': False
	# }, {
		# 'class': 'uptobox',
		# 'netloc': ['uptobox.com'],
		# 'host': ['Uptobox'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'v_vids',
		# 'netloc': ['v-vids.com'],
		# 'host': ['V-vids'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'vaughnlive',
		# 'netloc': ['vaughnlive.tv', 'breakers.tv', 'instagib.tv', 'vapers.tv']
	# }, {
		# 'class': 'veehd',
		# 'netloc': ['veehd.com']
	# }, {
		# 'class': 'veetle',
		# 'netloc': ['veetle.com']
	# }, {
		# 'class': 'vidbull',
		# 'netloc': ['vidbull.com'],
		# 'host': ['Vidbull'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'videomega',
		# 'netloc': ['videomega.tv'],
		# #'host': ['Videomega'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'videopremium',
		# 'netloc': ['videopremium.tv', 'videopremium.me']
	# }, {
		# 'class': 'videoweed',
		# 'netloc': ['videoweed.es'],
		# 'host': ['Videoweed'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'vidlockers',
		# 'netloc': ['vidlockers.ag'],
		# 'host': ['Vidlockers'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'vidspot',
		# 'netloc': ['vidspot.net'],
		# 'host': ['Vidspot'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'vidto',
		# 'netloc': ['vidto.me'],
		# 'host': ['Vidto'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'vidzi',
		# 'netloc': ['vidzi.tv'],
		# 'host': ['Vidzi'],
		# 'quality': 'Low',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'vimeo',
		# 'netloc': ['vimeo.com']
	# }, {
		# 'class': 'vk',
		# 'netloc': ['vk.com']
	# #}, {
	# #	'class': 'vodlocker',
	# #	'netloc': ['vodlocker.com'],
	# #	'host': ['Vodlocker'],
	# #	'quality': 'Low',
	# #	'captcha': False,
	# #	'a/c': False
	# }, {
		# 'class': 'xfileload',
		# 'netloc': ['xfileload.com'],
		# 'host': ['Xfileload'],
		# 'quality': 'High',
		# 'captcha': True,
		# 'a/c': False
	# }, {
		# 'class': 'xvidstage',
		# 'netloc': ['xvidstage.com'],
		# 'host': ['Xvidstage'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'youtube',
		# 'netloc': ['youtube.com'],
		# 'host': ['Youtube'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'zettahost',
		# 'netloc': ['zettahost.tv'],
		# 'host': ['Zettahost'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'zstream',
		# 'netloc': ['zstream.to'],
		# 'host': ['zStream'],
		# 'quality': 'Medium',
		# 'captcha': False,
		# 'a/c': False
	# }, {
		# 'class': 'watch1080p',
		# 'netloc': ['watch1080p.com'],
		# 'host': ['watch1080p'],
		# 'quality': 'High',
		# 'captcha': False,
		# 'a/c': False
	# }]
