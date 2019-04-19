# -*- coding: utf-8 -*-

#########################################################################################################
#
# Direct scraper
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
		self.ver = '0.0.4'
		self.update_date = 'Jan. 11, 2019'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.logo = 'https://i.imgur.com/nbtnvDr.png'
		self.name = name
		self.host = ['imdb.com','media-imdb.com','einthusan.tv','vimeocdn.com','apple.com','akamaized.net','micetop.us','vidcdn.pro','fbcdn.net','cmovieshd.com', 'vcstream.to', 'documentarymania.com','3donlinefilms.com','3dmoviesfullhd.com','totaleclips.com','freedocufilms.com','cartoonhd.pw','cooltvseries.com']
		self.netloc = ['imdb.com','media-imdb.com','einthusan.tv','vimeocdn.com','apple.com','akamaized.net','micetop.us','vidcdn.pro','fbcdn.net','cmovieshd.com', 'vcstream.to', 'documentarymania.com','3donlinefilms.com','3dmoviesfullhd.com','totaleclips.com','freedocufilms.com','cartoonhd.pw','cooltvseries.com']
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
		
	def createMeta(self, url, provider, logo, quality, links, key, riptype, vidtype='Movie', lang='en', sub_url=None, txt='', file_ext = '.mp4', testing=False, poster=None, headers=None, page_url=None):
	
		files_ret = []
		orig_url = url
		
		if testing == True:
			links.append(url)
			return links
			
		if control.setting('Host-%s' % name) == False:
			log('INFO','createMeta','Host Disabled by User')
			return links
			
		try:
			items = self.process(url, quality, riptype, headers, page_url)
			seq = 0
			
			for item in items:
				
				vidurl = item['src']
				durl = url
				
				allowsStreaming = item['allowsStreaming']
				allowsDownload = item['allowsDownload']
				quality = item['quality']
				riptype = item['riptype']
				fs = item['fs']
				online = item['online']
				params = item['params']
				urldata = item['urldata']
				
				try:
					log(type='INFO',method='createMeta', err=u'durl:%s ; res:%s; fs:%s' % (durl,quality,fs))
					files_ret.append({'source':self.name, 'maininfo':txt, 'titleinfo':'', 'quality':quality, 'vidtype':vidtype, 'rip':riptype, 'provider':provider, 'orig_url':orig_url, 'url':vidurl, 'durl':durl, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'poster':poster, 'subdomain':client.geturlhost(url), 'page_url':page_url, 'misc':{'player':'eplayer', 'gp':True}, 'seq':seq})
				except Exception as e:
					log(type='ERROR',method='createMeta', err=u'%s' % e)
					files_ret.append({'source':urlhost, 'maininfo':txt, 'titleinfo':'', 'quality':quality, 'vidtype':vidtype, 'rip':'Unknown' ,'provider':provider, 'orig_url':orig_url, 'url':vidurl, 'durl':url, 'urldata':urldata, 'params':params, 'logo':logo, 'online':online, 'allowsDownload':allowsDownload, 'resumeDownload':self.resumeDownload, 'allowsStreaming':allowsStreaming, 'key':key, 'enabled':True, 'fs':int(fs), 'file_ext':file_ext, 'ts':time.time(), 'lang':lang, 'sub_url':sub_url, 'poster':poster, 'subdomain':client.geturlhost(url), 'page_url':page_url, 'misc':{'player':'eplayer', 'gp':True}, 'seq':seq})
				seq += 1
				
		except Exception as e:
			log(type='ERROR', err="createMeta : %s" % e.args)
			
		for fr in files_ret:
			if fr != None and 'key' in fr.keys():
				control.setPartialSource(fr,self.name)
				links.append(fr)

		if len(files_ret) > 0:
			log('SUCCESS', 'createMeta', 'Successfully processed %s link >>> %s' % (provider, orig_url), dolog=self.init)
		else:
			log('FAIL', 'createMeta', 'Failed in processing %s link >>> %s' % (provider, orig_url), dolog=self.init)
			
		log('INFO', 'createMeta', 'Completed', dolog=self.init)
		
		return links
		
	def resolve(self, url, page_url=None, **kwargs):
		return resolve(url, page_url=page_url)
			
	def resolveHostname(self, host):
		return self.name
		
	def testLink(self, url):
		return check(url)
		
	def process(self, url, q, r, headers, page_url):
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
					
					items.append({'quality':q, 'riptype':r, 'src':u, 'fs':fs, 'online':online, 'params':params, 'urldata':urldata, 'allowsStreaming':True, 'allowsDownload':True})
					
			elif '3donlinefilms.com' in url or '3dmoviesfullhd.com' in url or 'freedocufilms.com' in url:
				data = urlparse.parse_qs(url)
				headers = {}
				
				if '3donlinefilms.com' in url:
					headers['Referer'] = 'http://3donlinefilms.com'
					l0 = 'https://3donlinefilms.com/update.php'
				elif 'freedocufilms.com' in url:
					headers['Referer'] = 'http://freedocufilms.com'
					l0 = 'https://freedocufilms.com/update.php'
				else:
					headers['Referer'] = 'http://3dmoviesfullhd.com'
					l0 = 'https://3dmoviesfullhd.com/update.php'
					
				page = data['page'][0]
				cook = client.request(page, output='cookie')
				post_data = {'file':data['src_file'][0]}
				
				cookie = '%s; zeroday=; visit=yes; jwplayer.qualityLabel=HD' % cook
				headers['Referer'] = page
				headers['User-Agent'] = client.agent()
				headers['Cookie'] = cookie
				
				u = data['file'][0]
				u = u.replace('//freedocufilms','//www.freedocufilms')
	
				try:
					ret = client.request(l0, post=client.encodePostData(post_data),headers=headers, output='extended', XHR=True, cookie=cookie)
				except Exception as e:
					log(type='FAIL', method='process', err='%s' % e, dolog=False, logToControl=False, doPrint=True)
				
				ret = client.request(u, output='headers', headers=headers, XHR=True)
				
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
				
				items.append({'quality':q, 'riptype':r, 'src':url, 'fs':fs, 'online':online, 'params':params, 'urldata':urldata, 'allowsStreaming':False, 'allowsDownload':True})
			elif 'cooltvseries.com' in url:
				urlx = client.request(url, output='geturl', headers=headers)
				urlx = '%s?e=file.mp4' % urlx
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
				allowsDownload = True
				items.append({'quality':q, 'riptype':r, 'src':urlx, 'fs':fs, 'online':online, 'params':params, 'urldata':urldata, 'allowsStreaming':True, 'allowsDownload':allowsDownload})
			else:
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
				allowsDownload = True
				if '.m3u8' in url:
					allowsDownload = False
				items.append({'quality':q, 'riptype':r, 'src':url, 'fs':fs, 'online':online, 'params':params, 'urldata':urldata, 'allowsStreaming':True, 'allowsDownload':allowsDownload})
					
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
			items.append({'quality':q, 'riptype':r, 'src':url, 'fs':fs, 'online':online, 'params':params, 'urldata':urldata, 'allowsStreaming':True, 'allowsDownload':True})
			
		return items
		
def qual_based_on_fs(q, fs):
	try:
		if int(fs) > 1.75 * float(1024*1024*1024):
			q = '1080p'
		elif int(fs) > 0.5 * float(1024*1024*1024):
			q = '720p'
		elif int(fs) < 0.3 * float(1024*1024*1024):
			q = '480p'
		else:
			q = '360p'
	except:
		pass
	return q

		
def T3DonlineFilms(url):
	error = ''
	try:
		data = urlparse.parse_qs(url)
		headers = {}
		
		if '3donlinefilms.com' in url:
			headers['Referer'] = 'https://3donlinefilms.com'
			l0 = 'https://3donlinefilms.com/update.php'
		elif 'freedocufilms.com' in url:
			headers['Referer'] = 'https://freedocufilms.com'
			l0 = 'https://freedocufilms.com/update.php'
		else:
			headers['Referer'] = 'https://3dmoviesfullhd.com'
			l0 = 'https://3dmoviesfullhd.com/update.php'
		
		u = data['file'][0]
		u = u.replace('//freedocufilms','//www.freedocufilms')
				
		page = data['page'][0]
		cook = client.request(page, output='cookie')
		
		post_data = {'file':data['src_file'][0]}
		
		cookie = '%s; zeroday=; visit=yes; jwplayer.qualityLabel=HD' % cook
		headers['Referer'] = data['page'][0]
		headers['User-Agent'] = client.agent()
		headers['Cookie'] = cookie
		
		try:
			ret = client.request(l0, post=client.encodePostData(post_data), output='extended', XHR=True, cookie=cookie)
		except:
			pass
		
		paramsx = {'headers':headers}
		params = client.b64encode(json.dumps(paramsx, encoding='utf-8'))
		
	except Exception as e:
		error = '%s' % e
	return u, error, params
	
def resolve(url, page_url=None, **kwargs):

	params = client.b64encode(json.dumps('', encoding='utf-8'))
	error = ''
	u = url
	if '3donlinefilms.com' in url or '3dmoviesfullhd.com' in url or 'freedocufilms.com' in url:
		u, error, params = T3DonlineFilms(url)
		return (u, error, params)
	else:
		if check(url) == False: 
			return (None, 'Error in check !', params)
	
	return (u, error, params)

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
