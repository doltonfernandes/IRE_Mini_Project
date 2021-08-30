import re
import xml.etree.ElementTree as xml
import xml.sax
import sys
import os

from dataHolder import DataHolder

class saxHandler(xml.sax.ContentHandler):

	def __init__(self):
		self.currTag = ""
		self.data = {
			'title': '',
			'infobox' : '',
			'body' : '',
			'category' : '',
			'link' : '',
			'reference': '',
		}
		# Since body is too big, we store strings in a list and then
		# concatenate using join(), which is much faster than +=
		self.body_list = []

	# Call when an element starts
	def startElement(self, tag, attributes):
		self.currTag = tag

	# Call when an elements ends
	def endElement(self, tag):
		if tag == "page":
			holder.insert(self.data)
			self.data['body'] = '\n'.join(self.body_list)
			for k in self.data:
				self.data[k] = ''
			self.body_list = []
			self.currTag = ""

	# Call when a character is read
	def characters(self, content):
		if self.currTag == 'title':
			self.data['title'] += content.lower().replace('"', "").replace("'", "").replace("_", "")
			return

		if self.currTag == 'text':
			contentLower = content.lower()
			# Check if infobox exists
			if re.search(r"{{infobox", contentLower):
				self.data['infobox'] += contentLower.replace('infobox', '').replace('"', "").replace("'", "").replace("_", "") + '\n'
				return
			# Check if category exists
			if re.search(r'\[\[category:', contentLower):
				self.data['category'] += contentLower.replace('[[category', '').replace('"', "").replace("'", "").replace("_", "") + '\n'
				return
			# Check if reference exists
			if re.search(r'{{cite', contentLower):
				self.data['reference'] += contentLower.replace(r'{{cite', '').replace('"', "").replace("'", "").replace("_", "") + '\n'
				return
			# Check if external exists
			if (contentLower.startswith('* [') or contentLower.startswith('*[')) and (re.search(r'http', contentLower) or re.search(r'www', contentLower)):
				self.data['link'] += contentLower.replace('"', "").replace("'", "").replace("_", "") + '\n'
				return
			# Add remaining text to body
			self.body_list.append(contentLower.replace('"', "").replace("'", "").replace("_", "") + '\n')

if not os.path.isdir(sys.argv[2]):
	os.mkdir(sys.argv[2])

parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
Handler = saxHandler()
parser.setContentHandler( Handler )

holder = DataHolder()
parser.parse(sys.argv[1])