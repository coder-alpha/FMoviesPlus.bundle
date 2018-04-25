import re,urllib,urlparse,base64,time,json

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import control
from resources.lib import resolvers


# Web Proxy
name = 'Anonymster'
loggertxt = []
PROXY_URL = "https://proxy.anonymster.com/browse.php?b=2&u="

class proxy:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Dec. 19, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.base_link = 'https://proxy.anonymster.com'
		self.name = name
		self.loggertxt = []
		self.disabled = False
		self.captcha = False
		self.ssl = True
		self.speedtest = 0
		self.headers = {'Connection' : 'keep-alive', 'User-Agent' : client.randomagent()}
		self.working = self.testSite()
		log(type='INFO', method='init', err=' -- Initializing %s %s %s End --' % (name, self.ver, self.update_date))
		
	def getLog(self):
		self.loggertxt = loggertxt
		return self.loggertxt
		
	def testSite(self):
		try:
			if self.disabled == True:
				log('INFO','testSite', 'Plugin Disabled')
				return False
				
			x1 = time.time()
			http_res = client.request(url=self.base_link, output='responsecode')
			self.speedtest = time.time() - x1
			
			if http_res in client.HTTP_GOOD_RESP_CODES:
				log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link))
				return True
				
			log('ERROR', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link))
			return False
		except Exception as e:
			log('ERROR','testSite', '%s' % e)
			return False
		
	def request(self, url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, use_web_proxy=False, XHR=False, IPv4=False):
	
		if self.working == False:
			log("Proxy working status is %s" % self.working)
			return None
	
		if headers == None:
			headers = self.headers

		return requestdirect(url=url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, XHR=XHR, IPv4=IPv4)
			
def requestdirect(url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, use_web_proxy=False, XHR=False, IPv4=False):

	try:
		urlhost = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
		
		if headers == None:
			headers = {'Connection' : 'keep-alive'}
			headers['User-Agent'] = client.randomagent()
		
		res = client.request(url = PROXY_URL + url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, XHR=XHR, IPv4=IPv4)
		
		page_data_string = client.getPageDataBasedOnOutput(res, output)
		
		#print page_data_string
		
		pattern = re.compile('<script[\s\S]+?/script>')
		page_data_string = re.sub(pattern, '', page_data_string)
			
		try:
			page_data_string = page_data_string.replace('\n','')	
			#page_data_string = page_data_string.replace('\r','r').replace('\n','<br/>').replace('\w','').replace('\.','').replace('\t','').replace('\ ','')
		except Exception as e:
			log('FAIL','requestdirect-1', '%s' % e, dolog=False)
			
		#print page_data_string

		try:
			page_data_stringx = json.dumps(page_data_string)
			page_data_stringx = page_data_stringx.replace('\\','')
			page_data_stringx = page_data_stringx[1:-1]
			page_data_string = page_data_stringx
		except Exception as e:
			log('FAIL','requestdirect-2', '%s' % e, dolog=False)
		
		#print page_data_string
		#page_data_string = str(page_data_string)
		
		try:
			r = unicode(page_data_string, "utf-8")
			page_data_string = r
		except Exception as e:
			log('FAIL','requestdirect-3', '%s' % e, dolog=False)
			try:
				r = str(page_data_string)
				page_data_string = r
			except Exception as e:
				log('FAIL','requestdirect-4', '%s' % e, dolog=False)
		
		page_data_string = page_data_string.replace('https://proxy.anonymster.com/browse.php?', '')
		page_data_string = page_data_string.replace('/browse.php?u=', '')
		page_data_string = page_data_string.replace('&amp;b=2', '')
		page_data_string = page_data_string.replace('b=2', '')
		page_data_string = page_data_string.replace('u=', '')
		page_data_string = page_data_string.replace('&http', 'http')
		page_data_string = page_data_string.replace('/http', 'http')
		
		try:
			page_data_string = page_data_string.decode('utf-8')
		except:
			pass
		try:
			page_data_string = urllib.unquote_plus(page_data_string)
		except:
			pass
		try:
			page_data_string = page_data_string.encode('utf-8')
		except:
			pass
		
		return client.getResponseDataBasedOnOutput(page_data_string, res, output)
		
	except Exception as e:
		log('ERROR','requestdirect', '%s' % e)
		return None

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