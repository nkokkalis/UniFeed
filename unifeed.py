#!/usr/bin/env python

import urllib2
from HTMLParser import HTMLParser
import datetime
import re
import xml.etree.ElementTree as et

class UnipiParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		
		self.innorm = False
		self.ina = False
		self.infont = False
		self.table_depth = 0
		self.font_depth = 0
		
		self.articles = []
	
	def handle_starttag(self, tag, attrs):
		if tag == 'table':
			if self.innorm:
				self.table_depth += 1
			else:
				for attr in attrs:
					if attr[0] == 'class' and attr[1] == 'norm':
						self.table_depth = 1
						self.innorm = True

		if tag == 'font' and self.innorm:
			self.infont = True
			self.font_depth += 1

		if tag == 'a' and self.infont:
			self.ina = True
			for attr in attrs:
				if attr[0] == 'href':
					self.articles.append(attr[1])
			
	
	def handle_endtag(self, tag):
		if tag == 'table':
			self.table_depth -=1
			if self.table_depth == 0:
				self.innorm = False

		if tag == 'font':
			self.font_depth -= 1
			if self.font_depth == 0:
				self.infont = False

		if tag == 'a':
			self.ina = False

class Stripper(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.ob = ''
	def handle_data(self, data):
		self.ob += data
        
def strip(html):
    s = Stripper()
    s.feed(html)
    return s.ob

html = urllib2.urlopen('http://www.unipi.gr').read()
parser = UnipiParser()
parser.feed(html)

root = et.Element('feed')
root.set('xmlns', 'http://www.w3.org/2005/Atom')

global_title_node = et.SubElement(root, 'title')
global_title_node.text = 'Unipi feed'
icon_node = et.SubElement(root, 'icon')
icon_node.text = 'http://www.unipi.gr/favicon.ico'
global_id_node = et.SubElement(root, 'id')
global_id_node.text = 'urn:students.cs.unipi.gr-feed'
global_updated_node = et.SubElement(root, 'updated')
global_updated_node.text = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%SZ')

for url in parser.articles:
	html = urllib2.urlopen('http://www.unipi.gr/%s' % url).read()
	html = html[html.find('smaplev2') + 5:]
	title = re.findall('<p class="smaplev2">(.*?)</p>', html, re.S)[0].decode('cp1253')
	title = strip(title)
	datestr = re.findall('<p class="smaplev2">.*?</p>.*?<p>.*?<strong>(.*?)</strong>.*?</p>', html, re.S)[0].strip().decode('cp1253')
	date = datetime.datetime.strptime(datestr, '%d/%m/%Y')
	content = re.findall('<td class="norm"><p class="smaplev2">.*?</p>.*?<p>.*?</p>(.*?)</td>', html, re.S)[0].strip().decode('cp1253')
	id = url.split('=')[-1]
	
	entry_node = et.SubElement(root, 'entry')
	title_node = et.SubElement(entry_node, 'title', type="html")
	title_node.text = title
	link_node = et.SubElement(entry_node, 'link')
	link_node.set('href', 'http://www.unipi.gr/%s' % url)
	id_node = et.SubElement(entry_node, 'id')
	id_node.text = 'urn:article-%s' % id
	updated_node = et.SubElement(entry_node, 'updated')
	updated_node.text = date.strftime('%Y-%m-%dT00-00-00Z')
	summary_node = et.SubElement(entry_node, 'content', mode="escaped", type="text/html")
	summary_node.text = content
	
tree = et.ElementTree(root)
tree.write('miou.atom', encoding="utf-8")
