# -*- coding: utf-8 -*-

#########################################################################################################
#
# Direct scrapper
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

import re,urllib,json,time,urlparse
import os,sys,ast

from resources.lib.libraries import client, control, source_utils

hdr = {
	'User-Agent': client.USER_AGENT,
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}

name = 'direct'
loggertxt = []
	
class host:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Dec. 16, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.logo = 'https://i.imgur.com/nbtnvDr.png'
		self.name = name
		self.host = ['imdb.com','media-imdb.com','einthusan.tv','vimeocdn.com','apple.com','akamaized.net','micetop.us','vidcdn.pro','fbcdn.net','cmovieshd.com', 'vcstream.to', 'documentarymania.com','3donlinefilms.com']
		self.netloc = ['imdb.com','media-imdb.com','einthusan.tv','vimeocdn.com','apple.com','akamaized.net','micetop.us','vidcdn.pro','fbcdn.net','cmovieshd.com', 'vcstream.to', 'documentarymania.com','3donlinefilms.com']
		self.quality = '1080p'
		self.loggertxt = []
		self.captcha = False
		self.allowsDownload = True
		self.resumeDownload = True
		self.allowsStreaming = True
		self.ac = False
		self.pluginManagedPlayback = False
		self.speedtest = 'NA'
		self.working = True
		self.resolver = True
		self.msg = ''
		self.init = True
		log(type='INFO', method='init', err=' -- Initializing %s %s %s End --' % (name, self.ver, self.update_date))

	def info(self):
		return {
			'name': self.name,
			'ver': self.ver,
			'date': self.update_date,
			'class': self.name,
			'speed': self.speedtest,
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
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, vidtype='Movie', lang='en', sub_url=None, txt='', file_ext = '.mp4', testing=False, poster=None, headers=None):
	
		if testing == True:
			links.append(url)
			return links
			
		if control.setting('Host-%s' % name) == False:
			log('INFO','createMeta','Host Disabled by User')
			return links
			
		orig_url = url
			
		files_ret = []
		
		items = self.process(url, quality, riptype, headers)
		
		for item in items:
		
			url = item['src']
			quality = item['quality']
			riptype = item['riptype']
			fs = item['fs']
			online = item['online']
			params = item['params']
			urldata = item['urldata']
			
			try:
				files_ret.append({'source':self.name, 'maininfo':txt, 'titleinfo':'', 'quality':quality, 'vidtype':vidtype, 'rip':riptype, 'provider':provider, 'url':url, 'durl':url, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'poster':poster, 'subdomain':client.geturlhost(url), 'misc':{'player':'eplayer', 'gp':True}})
			except Exception as e:
				log(type='ERROR',method='createMeta', err=u'%s' % e)
				files_ret.append({'source':urlhost, 'maininfo':txt, 'titleinfo':'', 'quality':quality, 'vidtype':vidtype, 'rip':'Unknown' ,'provider':provider, 'url':url, 'durl':url, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':self.allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':self.allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'poster':poster, 'subdomain':client.geturlhost(url), 'misc':{'player':'eplayer', 'gp':True}})
			
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
		
	def process(self, url, q, r, headers):
		items = []
		
		try:
			if 'vcstream.to' in url:
				id = re.compile('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)').findall(url)[0]
				headersx = {'Referer': url, 'User-Agent': client.agent()}
				page_data = client.request('https://vcstream.to/player?fid=%s&page=embed' % id, headers=headersx)
				srcs = re.findall(r'sources:.\[(.*?)\]', page_data)[0]
				srcs = srcs.replace('\\n','').replace('\\','')
				srcs = '''[%s]''' % srcs
				j_data = json.loads(srcs)
				for j in j_data:
					t = j['name']
					label = j['label']
					u = j['src']
					if label.lower() == 'raw':
						q = source_utils.check_sd_url(t)
					else:
						q = label
					r = source_utils.check_sd_url_rip(t)
					
					fs = client.getFileSize(u, retry429=True, headers=headers)
					if fs == None or int(fs) == 0:
						fs = client.getFileSize(u, retry429=True)
					q = qual_based_on_fs(q,fs)
					online = check(u)
					urldata = client.b64encode(json.dumps('', encoding='utf-8'))
					params = client.b64encode(json.dumps('', encoding='utf-8'))
					if headers != None:
						paramsx = {'headers':headers}
						params = client.b64encode(json.dumps(paramsx, encoding='utf-8'))
					
					items.append({'quality':q, 'riptype':r, 'src':u, 'fs':fs, 'online':online, 'params':params, 'urldata':urldata})
					
			elif '3donlinefilms.com' in url:
				data = urlparse.parse_qs(url)
				headers = {}
				headers['Referer'] = 'http://3donlinefilms.com'
				b = data['page'][0]
				cook = client.request(b, output='cookie')
				
				l0 = 'http://3donlinefilms.com/update.php'
				post_data = {'file':data['src_file'][0]}
				
				cookie = '%s; zeroday=; visit=yes; jwplayer.qualityLabel=HD' % cook
				headers['Referer'] = data['page'][0]
				headers['User-Agent'] = client.agent()
				headers['Cookie'] = cookie
				
				try:
					ret = client.request(l0, post=client.encodePostData(post_data), output='extended', XHR=True, cookie=cookie)
				except:
					pass
				
				u = '%s?file=%s' % (data['file'][0], data['src_file'][0].replace(' ',''))
				ret = client.request(u, headers=headers, output='headers')
				try:
					fs = int(re.findall(r'Content-Length:(.*)', str(ret), re.MULTILINE)[0].strip())
				except:
					fs = 0

				q = qual_based_on_fs(q,fs)

				online = False
				if int(fs) > 0:
					online = True
					
				urldata = client.b64encode(json.dumps('', encoding='utf-8'))
				paramsx = {'headers':headers}
				params = client.b64encode(json.dumps(paramsx, encoding='utf-8'))
				
				items.append({'quality':q, 'riptype':r, 'src':url, 'fs':fs, 'online':online, 'params':params, 'urldata':urldata})
					
		except Exception as e:
			log(type='ERROR',method='process', err=u'%s' % e)

		if len(items) == 0:
			fs = client.getFileSize(url, retry429=True, headers=headers)
			if fs == None or int(fs) == 0:
				fs = client.getFileSize(url, retry429=True)
			q = qual_based_on_fs(q,fs)
			online = check(url)
			urldata = client.b64encode(json.dumps('', encoding='utf-8'))
			params = client.b64encode(json.dumps('', encoding='utf-8'))
			if headers != None:
				paramsx = {'headers':headers}
				params = client.b64encode(json.dumps(paramsx, encoding='utf-8'))
			items.append({'quality':q, 'riptype':r, 'src':url, 'fs':fs, 'online':online, 'params':params, 'urldata':urldata})
			
		return items
		
def qual_based_on_fs(q,fs):
	try:
		if int(fs) > 2 * float(1024*1024*1024):
			q = '1080p'
		elif int(fs) > 1 * float(1024*1024*1024):
			q = '720p'
	except:
		pass
	return q

		
def T3DonlineFilms(url):
	error = ''
	try:
		data = urlparse.parse_qs(url)
		headers = {}
		headers['Referer'] = 'http://3donlinefilms.com'
		b = data['page'][0]
		cook = client.request(b, output='cookie')
		
		l0 = 'http://3donlinefilms.com/update.php'
		post_data = {'file':data['src_file'][0]}
		
		cookie = '%s; zeroday=; visit=yes; jwplayer.qualityLabel=HD' % cook
		headers['Referer'] = data['page'][0]
		headers['User-Agent'] = client.agent()
		headers['Cookie'] = cookie
		
		try:
			ret = client.request(l0, post=client.encodePostData(post_data), output='extended', XHR=True, cookie=cookie)
		except:
			pass
		
		u = '%s?file=%s' % (data['file'][0], data['src_file'][0].replace(' ',''))
		
		paramsx = {'headers':headers}
		params = client.b64encode(json.dumps(paramsx, encoding='utf-8'))
	except Exception as e:
		error = '%s' % e
	return u, params, error
	
def resolve(url):

	params = client.b64encode(json.dumps('', encoding='utf-8'))
	error = ''
	u = url
	if '3donlinefilms.com' in url:
		u, params, error = T3DonlineFilms(url)
		return u, params, error
	else:
		if check(url) == False: 
			return None, params, 'Error in check !'
	
	return u, params, error

	
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
