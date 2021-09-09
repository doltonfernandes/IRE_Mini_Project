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
		self.infoboxCnt = 0

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
		contentLower = content.lower()
		if self.currTag == 'title':
			# Check if title exists
			self.data['title'] += contentLower.replace('"', "").replace("'", "").replace("_", "")
			return

		if self.currTag == 'text':
			# Check if infobox exists
			if self.infoboxCnt > 0 or re.search(r"{{infobox", contentLower):
				if contentLower.strip() == '}}':
					self.infoboxCnt = 0
					return
				if self.infoboxCnt == 0:
					self.data['infobox'] += contentLower.replace('infobox', '').replace('"', "").replace("'", "").replace("_", "") + '\n'
				else:
					self.data['infobox'] += contentLower.replace('"', "").replace("'", "").replace("_", "") + '\n'
				self.infoboxCnt = 1
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

parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
Handler = saxHandler()
parser.setContentHandler(Handler)

if not os.path.exists(sys.argv[2]):
	os.makedirs(sys.argv[2])

if not os.path.exists(sys.argv[2] + '/Tempfiles'):
	os.makedirs(sys.argv[2] + '/Tempfiles')

holder = DataHolder(sys.argv[2], sys.argv[3])
parser.parse(sys.argv[1])
holder.saveOne()
holder.mergeFiles()
holder.splitInvIdx()
holder.saveStats()