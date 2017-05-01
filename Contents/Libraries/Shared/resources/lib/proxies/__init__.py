


import re,urllib,urlparse,pkgutil

from resources.lib.libraries import client
from resources.lib.libraries import control
	
sourceProxies = []
sourceProxiesCaller = []

def init():
	
	del sourceProxies[:]
	del sourceProxiesCaller[:]
	
	for package, name, is_pkg in pkgutil.walk_packages(__path__):	
		try:
			c = __import__(name, globals(), locals(), [], -1).proxy()
			print "Adding Proxy %s : %s to Interface" % (c.name, c.base_link)
			sourceProxies.append({'name': c.name, 'url': c.base_link, 'captcha':c.captcha, 'SSL':c.ssl, 'working':c.working, 'speed':round(c.speedtest,3)})
			sourceProxiesCaller.append({'name': c.name, 'url': c.base_link, 'captcha':c.captcha, 'working':c.working, 'speed':round(c.speedtest,3), 'call': c})
		except Exception as e:
			print "Error: %s - %s" % (name, e)
			pass
			
def info():
	return sourceProxies
	
def checkRet(ret, output):
	if (output != 'extended' and ret != None) or (output == 'extended' and ret[0] != None):
		return True
	elif (output != 'response' and ret != None) or (output == 'response' and ret[0] != None):
		return True
	elif (output != 'responsecodeext' and ret != None) or (output == 'responsecodeext' and ret[0] != None):
		return True
	elif ret != None:
		return True

	return False
	
def request(url, proxy_name=None, proxy_url=None, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, use_web_proxy=False, proxy_options=None, use_web_proxy_as_backup=False, XHR=False):

# output extended = 4, response = 2, responsecodeext = 2
	#try:
	ret = None
	if use_web_proxy != True or use_web_proxy_as_backup == True:
		try:
			ret = client.request(url=url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, XHR=XHR)
		except:
			if output == 'extended':
				ret = (None, None, None, None)
			elif output == 'response' or output == 'responsecodeext':
				ret = (None, None)
			else:
				ret = None
		
	if checkRet(ret, output):
		return ret
	elif use_web_proxy == True and proxy_options == None and proxy_name != None and proxy_url != None:
		print "Trying 1-proxy_options == None. len(sourceProxiesCaller) = %s" % len(sourceProxiesCaller)
		for proxy in sourceProxiesCaller:
			if proxy_name == proxy['name'] and proxy_url == proxy['url']:
				print "Trying %s for %s" % (proxy['name'], url)
				ret = proxy['call'].request(url=url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, XHR=XHR)
				if checkRet(ret, output):
					return ret
	elif use_web_proxy == True and proxy_options != None:
		print "Trying 2-proxy_options != None. len(sourceProxiesCaller) = %s" % len(sourceProxiesCaller)
		for proxyo in proxy_options:
			for proxy in sourceProxiesCaller:
				if proxyo['name'] == proxy['name'] and proxyo['url'] == proxy['url']:
					print "Trying %s for %s" % (proxy['name'], url)
					ret = proxy['call'].request(url=url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, XHR=XHR)
					if checkRet(ret, output):
						return ret
	elif (use_web_proxy == True and proxy_options == None and proxy_name==None and proxy_url==None) or use_web_proxy_as_backup == True:
		print "Trying 3-proxy_options == None. len(sourceProxiesCaller) = %s" % len(sourceProxiesCaller)
		for proxy in sourceProxiesCaller:
			print "Trying %s for %s" % (proxy['name'], url)
			ret = proxy['call'].request(url=url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, XHR=XHR)
			if checkRet(ret, output):
				return ret
			
	if output == 'extended':
		return (None, None, None, None)
	elif output == 'response' or output == 'responsecodeext':
		return (None, None)
	return None
	# except Exception as e:
		# print ('ERROR proxies request > %s url %s' % (e.args, url))
		# return None