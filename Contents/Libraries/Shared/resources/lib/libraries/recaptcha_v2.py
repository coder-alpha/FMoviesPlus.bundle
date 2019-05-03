# -*- coding: utf-8 -*-
# Coder Alpha
# https://github.com/coder-alpha
#

"""
	Copyright (C) 2019 coder-alpha

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

"""

import re,urllib,urlparse,json,random,time,base64,os
import client, control

UR = []

name = 'recaptcha_v2'
loggertxt = []

class UnCaptchaReCaptcha:
	
	def __init__(self, *args, **kwargs):
		self.max_iter = 1
		self.sitekey = "6Lc50JwUAAAAAAVVXOTavycUhRtMGphLfi3sj0v6"
		self.lang = "en"
		self.baseUrl = "https://fmovies.taxi/"
		self.ajax = "user/ajax/menu-bar?ts=1556460000&_=740"
		self.captchaActive = False
		self.cval = None
		self.waf = "waf-verify"
		self.cookie = None
		self.ua = client.agent() #"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0"
		self.headers = {'User-Agent':self.ua}
		
	def init(self):
		init()
		
	def setBaseUrl(self, baseURL):
		self.baseUrl = baseURL
		
	def captchaStatus(self):
		#print self.headers
		err = ''
		html, r2, r3, r4 = self.testSiteReq()
		
		if self.captchaActive == False:
			self.cookie = self.getCookies()
		
		return self.captchaActive, html, self.cookie, self.ua, err, self.baseUrl
		
	def formatCookie(self, cookie):
		cookS = cookie.split(';')
		cookA = []
		for c in cookS:
			if '=' in c:
				if 'expire' in c or 'httponly' in c.lower() or 'path' in c or 'domain' in c:
					pass
				else:
					cookA.append(c.strip())
		cookA = list(set(cookA))
		return '; '.join(x for x in cookA)
		
	def getCookies(self):
		self.headers['Referer'] = self.baseUrl
		self.headers['Cookie'] = self.cookie
		r = client.request(urlparse.urljoin(self.baseUrl,self.ajax), output='extended', headers=self.headers)
		if isinstance(r, tuple) and len(r) == 4:
			html, r2, r3, r4 = r
			#print r3, r4

			if 'Cookie' in r2.keys() and 'session' in r2['Cookie']:
				self.cookie += '; ' + r2['Cookie']
				self.headers['Cookie'] = self.cookie
			else:
				try:
					session = re.findall(r'Set-Cookie:(.*?)\n', str(r3))[0].strip()
					if 'session' in session:
						self.cookie += '; ' + session
				except:
					pass
					
		return self.formatCookie(self.cookie)
		
	def testSiteReq(self):
		self.headers['Referer'] = self.baseUrl
		html, r2, r3, r4 = client.request(self.baseUrl, headers=self.headers, output='extended')
		#print r2, r3, r4
		#print html[:200]
		
		try:
			self.cookie = r4
			if self.cookie == None or len(self.cookie) == 0:
				try:
					self.cookie = re.findall(r'Set-Cookie:(.*?)\n', str(r3))[0].strip()
					self.cookie = self.formatCookie(self.cookie)
				except:
					pass
		except:
			pass
		
		e = "Retrieved cookie: %s" % self.cookie
		log(type='INFO', method='testSiteReq', err='%s' % e, dolog=True, logToControl=True, doPrint=True)
		
		self.captchaActive = False
		if 'Please complete the security check to continue!' in html:
			self.captchaActive = True
			try:
				self.sitekey = client.parseDOM(html, 'div', attrs={'class':'g-recaptcha'}, ret='data-sitekey')[0]
			except:
				e = 'Could not find data-sitekey'
				log(type='ERROR', method='testSiteReq', err='%s' % e, dolog=True, logToControl=True, doPrint=True)
		else:
			self.captchaActive = False
			
		return html, r2, r3, r4
			
	def retData(self):
		return self.processCaptcha(key=self.sitekey, lang=self.lang)
		
	def processCaptcha(self, key, lang, referer=None):
		if referer is None: referer = self.baseUrl
		headers = {'Referer': referer, 'Accept-Language': self.lang, 'User-Agent':self.ua}
		for k in headers.keys():
			self.headers[k] = headers[k]
		
		html, r2, r3, r4 = client.request('https://www.google.com/recaptcha/api/fallback?k=%s' % (key), headers=self.headers, output='extended')
		
		#print r2, r3, r4
		token = None
		payload = re.findall('"(/recaptcha/api2/payload[^"]+)', html)

		message = re.findall('<label[^>]+class="fbc-imageselect-message-text"[^>]*>(.*?)</label>', html)
		if not message:
			message = re.findall('<div[^>]+class="fbc-imageselect-message-error">(.*?)</div>', html)
		if not message:
			token = re.findall('"this\.select\(\)">(.*?)</textarea>', html)[0]
			if token:
				e = ('Captcha Success: %s' % (token))
				log(type='INFO', method='processCaptcha', err='%s' % e, dolog=True, logToControl=True, doPrint=True)
				pass
			else:
				e = ('Captcha Failed: %s')
				log(type='INFO', method='processCaptcha', err='%s' % e, dolog=True, logToControl=True, doPrint=True)
				pass
		else:
			message = message[0]
			payload = payload[0]

		self.cval = re.findall('name="c"\s+value="([^"]+)', html)[0]
		captcha_imgurl = 'https://www.google.com%s' % (payload.replace('&amp;', '&'))
		e = "captcha_imgurl: %s" % captcha_imgurl
		log(type='INFO', method='processCaptcha', err='%s' % e, dolog=True, logToControl=False, doPrint=True)
		
		message = re.sub('</?(div|strong)[^>]*>', '', message)
		e = "message: %s" % message
		log(type='INFO', method='processCaptcha', err='%s' % e, dolog=True, logToControl=False, doPrint=True)

		captcha = {'message':message, 'payload':captcha_imgurl, 'cval':self.cval}
		
		if token == None:
			return captcha
		else:
			return token
			
	def solverAsk(self):
		txt = raw_input("Enter choices:")  
		return self.solveCaptcha(resp=txt.split(','))
			
	def solveCaptcha(self, resp, referer=None):
		if referer is None: referer = self.baseUrl
		headers = {'Referer': referer, 'Accept-Language': self.lang, 'User-Agent':self.ua}
		self.headers['Referer'] = referer
		#captcha_response = {"response":resp, "e":"BhIUo1BKAVNqQETlh4Iy3w8NMpA"}
		#data = {'c': cval, 'response': captcha_response}
		
		data = {'c':self.cval}
		postData = client.encodePostData(data) + '&response=' + ('&response='.join(str(x) for x in resp))
		#print postData
		error = ''
		html = ''
		ret = False
		
		try:
			url = "https://www.google.com/recaptcha/api/fallback?k=%s"
			r = client.request(url % (self.sitekey), post=postData, headers=headers, output='extended')
			if isinstance(r, tuple) and len(r) == 4:
				html, r2, r3, r4 = r
			else:
				raise Exception('HTTP Error: %s' % r)
		except Exception as e:
			error = '%s' % e
			log(type='INFO', method='solveCaptcha', err='%s' % e, dolog=True, logToControl=True, doPrint=True)
			
		#print r2, r3, r4
		
		if error == '' and 'Copy this code and paste it in the empty box below' in html:
			try:
				#print r2, r3, r4
				#print html
				
				#token = re.findall('"this\.select\(\)">(.*?)</textarea>', html)[0]
				token = re.findall(r'readonly>(.*?)<', html)[0]
				if token:
					e = ('Captcha Success !')
					log(type='INFO', method='solveCaptcha', err='%s' % e, dolog=True, logToControl=True, doPrint=True)
					#print token
					data = {'g-recaptcha-response': token}
					referer = self.baseUrl
					headers = {'User-Agent':self.ua}
					headers['Referer'] = referer
					headers['Cookie'] = self.cookie
					#print headers

					r = client.request(urlparse.urljoin(self.baseUrl, self.waf).replace('https:','http:'), post=client.encodePostData(data), output='extended', headers=headers, followredirect=False, redirect=False)
					if isinstance(r, tuple) and len(r) == 4:
						html, r2, r3, r4 = r
					else:
						raise Exception('HTTP Error: %s' % r)
					#print r2, r3, r4
					
					try:
						self.cookie += '; ' + re.findall(r'Set-Cookie:(.*?)\n', str(r3))[0].strip()
						self.cookie = self.formatCookie(self.cookie)
					except:
						pass
					
					headers['Cookie'] = self.cookie
					#print headers
					
					r = client.request(self.baseUrl, output='extended', headers=headers)
					if isinstance(r, tuple) and len(r) == 4:
						html, r2, r3, r4 = r
					else:
						raise Exception('HTTP Error: %s' % r)
					#print r2, r3, r4
					
					self.headers = headers

					if 'Cookie' in r2.keys() and 'session' in r2['Cookie']:
						self.cookie += '; ' + r2['Cookie']
						headers['Cookie'] = self.cookie
					else:
						try:
							self.cookie += '; ' + re.findall(r'Set-Cookie:(.*?)\n', str(r3))[0].strip()
							self.cookie = self.formatCookie(self.cookie)
						except:
							pass
						
					headers['Referer'] = self.baseUrl
					r = client.request(urlparse.urljoin(self.baseUrl,self.ajax), output='extended', headers=headers)
					if isinstance(r, tuple) and len(r) == 4:
						html, r2, r3, r4 = r
					else:
						raise Exception('HTTP Error: %s' % r)
					#print r2, r3, r4
					
					if 'Cookie' in r2.keys() and 'session' in r2['Cookie']:
						self.cookie += '; ' + r2['Cookie']
						headers['Cookie'] = self.cookie
					else:
						try:
							session = re.findall(r'Set-Cookie:(.*?)\n', str(r3))[0].strip()
							if 'session' in session:
								self.cookie += '; ' + session
							self.cookie = self.formatCookie(self.cookie)
						except:
							pass

					ret = True
				else:
					e = ('Captcha Failed !')
					log(type='INFO', method='solveCaptcha', err='%s' % e, dolog=True, logToControl=True, doPrint=True)
			except Exception as e:
				error = '%s' % e
				log(type='ERROR', method='solveCaptcha', err='%s' % e, dolog=True, logToControl=True, doPrint=True)
		else:
			if error != '':
				e = ('Captcha Error: %s !' % error)
				log(type='INFO', method='solveCaptcha', err='%s' % e, dolog=True, logToControl=True, doPrint=True)
			else:
				e = ('Captcha Failed !')
				log(type='INFO', method='solveCaptcha', err='%s' % e, dolog=True, logToControl=True, doPrint=True)
				
		self.cookie = self.formatCookie(self.cookie)
		return ret, html, self.cookie, self.ua, error, self.baseUrl

def init(baseurl=None):
	UU = UnCaptchaReCaptcha()
	if baseurl != None:
		UU.setBaseUrl(baseurl)
	del UR[:]
	UR.append(UU)
	
def getUR():
	if len(UR) == 0:
		init()
	return UR[0]
	
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
	
init()