#!/usr/bin/env python

import urllib2
from HTMLParser import HTMLParser
import datetime
import re

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

	def handle_startendtag(self, tag, attrs):
		pass

class UnipiInnerParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		
		self.innorm = False
		self.innormforrealz = False
		self.intitle = False
		self.intitleforrealz = False
		self.indate = False
		self.indateforrealz = False
		self.aftertitle = False
		self.frist = False

	def handle_starttag(self, tag, attrs):
		if tag == 'td':
			for attr in attrs:
				if attr[0] == 'class' and attr[1] == 'norm':
					if self.innorm:
						self.innormforrealz = True
					else:
						self.innorm = True

		if tag == 'p' and self.innorm:
			if self.aftertitle:
				self.indate = True
			else:
				for attr in attrs:
					if attr[0] == 'class' and attr[1] == 'smaplev2':
						if self.frist:
							self.intitle = True
						else:
							self.frist = True

		if tag == 'b' and self.intitle:
			self.intitleforrealz = True
		
		if tag == 'strong' and self.indate:
			self.indateforrealz = True
			
	def handle_startendtag(self, tag, attrs):
		pass
			
	def handle_data(self, data):
		if self.intitleforrealz:
			self.title = data.decode('cp1253')
		if self.indateforrealz:
			day = int(data.split('/')[0])
			month = int(data.split('/')[1])
			year = int(data.split('/')[2])
			self.date = datetime.date(year, month, day)

	
	def handle_endtag(self, tag):
		if tag == 'p':
			if self.intitle:
				self.intitle = False
				self.aftertitle = True
			elif self.indate:
				self.indate = False
				self.aftertitle = False
		
		if tag == 'td':
			self.innormforrealz = False

		if tag == 'b':
			self.intitleforrealz = False

		if tag == 'strong':
			self.indateforrealz = False

import xml.etree.ElementTree as et

html = urllib2.urlopen('http://www.unipi.gr').read()
parser = UnipiParser()
parser.feed(html)

root = et.Element('feed')
root.set('xmlns', 'http://www.w3.org/2005/Atom')

global_title_node = et.SubElement(root, 'title')
global_title_node.text = 'Unipi feed'
global_id_node = et.SubElement(root, 'id')
global_id_node.text = 'urn:students.cs.unipi.gr-feed'
global_updated_node = et.SubElement(root, 'updated')
global_updated_node.text = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%SZ')

for url in parser.articles:
	html = urllib2.urlopen('http://www.unipi.gr/%s' % url).read()
	parser = UnipiInnerParser()
	parser.feed(html)
	
	date = parser.date
	html = html[html.find('smaplev2') + 5:]
	title = re.findall('<p class="smaplev2">(.*?)</p>', html, re.S)[0].decode('cp1253')
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
tree.write('/var/www/html/unipi.atom', encoding="utf-8")
'''

<?xml version="1.0" encoding="utf-8"?>
 
<feed xmlns="http://www.w3.org/2005/Atom">
 
        <title>Example Feed</title>
        <subtitle>A subtitle.</subtitle>
        <link href="http://example.org/feed/" rel="self" />
        <link href="http://example.org/" />
        <id>urn:uuid:60a76c80-d399-11d9-b91C-0003939e0af6</id>
        <updated>2003-12-13T18:30:02Z</updated>
        <author>
                <name>John Doe</name>
                <email>johndoe@example.com</email>
        </author>
 
        <entry>
                <title>Atom-Powered Robots Run Amok</title>
                <link href="http://example.org/2003/12/13/atom03" />
                <link rel="alternate" type="text/html" href="http://example.org/2003/12/13/atom03.html"/>
                <link rel="edit" href="http://example.org/2003/12/13/atom03/edit"/>
                <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
                <updated>2003-12-13T18:30:02Z</updated>
                <content>Some text.</content>
        </entry>
 
</feed>'''
