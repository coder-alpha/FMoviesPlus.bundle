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


import re,unicodedata


def movie(title):
    title = re.sub('\n|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title


def tv(title):
    title = re.sub('\n|\s(|[(])(UK|US|AU|\d{4})(|[)])$|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title
	
def removeParanthesis(title):
	p = re.compile('(.())\(([^()]|())*\)')
	m = p.search(title)
	if m:
		title = title.replace(m.group(),'').strip()
	else:
		title = title.strip()
	return title
	
def removeParanthesisAndSeason(title,season):
	if len(title) > 5:
		otitle = title[:-4] + title[-4:].replace(str(season),'') # replace season no. from end only not if those chars are within the title
	elif len(title) > 3:
		otitle = title[:-2] + title[-2:].replace(str(season),'') # replace season no. from end only not if those chars are within the title
	else:
		otitle = title.replace(str(season),'')
	title = otitle
	if len(title) < 2:
		title = otitle
		
	title = removeParanthesis(title)

	return title.strip()
		
def tvWatchTitle(title,season,episode,etitle):

	title = removeParanthesis(title)
	
	if len(title) > 5:
		otitle = title[:-4] + title[-4:].replace(str(season),'') # replace season no. from end only not if those chars are within the title
	elif len(title) > 3:
		otitle = title[:-2] + title[-2:].replace(str(season),'') # replace season no. from end only not if those chars are within the title
	else:
		otitle = title.replace(str(season),'')
	title = otitle
	if len(title) < 2:
		title = otitle
		
	if etitle != None:
		if '-' in etitle:
			etitle = etitle.split('-')[1]
	else:
		etitle = ''
	etitle = etitle.strip()
		
	title = "%s - S%sE%s - %s" % (removeParanthesis(title),season,episode,etitle)
	return title

def get(title):
    if title == None: return
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\n|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title

def query(title):
    if title == None: return
    title = title.replace('\'', '').rsplit(':', 1)[0]
    return title

def query2(title):
    if title == None: return
    title = title.replace('\'', '').replace('-','')
    return title

def query10(title):
    if title == None: return
    title = title.replace('\'', '').replace(':','').replace('.','').replace(' ','-').lower()
    return title

def geturl(title):
    if title == None: return
    title = title.lower()
    title = title.translate(None, ':*?"\'\.<>|&!,')
    title = title.replace('/', '-')
    title = title.replace(' ', '+')
    title = title.replace('--', '-')
    title = title.replace('\'', '-')
    return title

def normalize(title):
    try:
        try: return title.decode('ascii').encode("utf-8")
        except: pass

        t = ''
        for i in title:
            c = unicodedata.normalize('NFKD',unicode(i,"ISO-8859-1"))
            c = c.encode("ascii","ignore").strip()
            if i == ' ': c = i
            t += c

        return t.encode("utf-8")
    except:
        return title

