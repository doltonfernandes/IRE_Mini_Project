import re
from nltk.stem import PorterStemmer
from collections import Counter
import os
from os import listdir
from os.path import isfile, join
import shutil

class DataHolder():
	def __init__(self, invertedIDXpath, statsPath):
		self.stopwords = {'have', 'more', 'will', 'further', 'but', \
						'this', 'her', 'myself', 'doing', 'didn', \
						'between', 'should', 'herself', 'because', \
						'few', 'hadn', 'hers', 'each', 'out', 'now', \
						'just', 'which', 'couldn', 'when', 'there', \
						'weren', 'then', 'does', 'our', 'hasn', \
						'were', 'those', 'are', 'don', 'aren', \
						'above', 'and', 'your', 'has', 'having', \
						'mustn', 'why', 'over', 'isn', 'can', \
						'most', 'both', 'been', 'own', 'you', \
						'theirs', 'against', 'they', 'about', \
						'same', 'only', 'himself', 'other', \
						'whom', 'what', 'did', 'themselves', \
						'their', 'shouldn', 'with', 'them', \
						'who', 'wouldn', 'mightn', 'being', \
						'before', 'for', 'ain', 'very', 'again', \
						'too', 'itself', 'until', 'during', \
						'where', 'yourself', 'his', 'through', \
						'shan', 'nor', 'not', 'below', 'under', \
						'ours', 'some', 'after', 'him', 'from', \
						'off', 'won', 'while', 'down', 'these', \
						'ourselves', 'its', 'such', 'yours', \
						'had', 'the', 'here', 'yourselves', \
						'wasn', 'was', 'haven', 'doesn', 'how', \
						'any', 'she', 'all', 'needn', 'that', \
						'into', 'than', 'once'}

		self.stemmer = PorterStemmer()
		self.pageCnt = 0
		self.currBlock = 0
		self.originalTokens = {}
		self.invertedIdx = {}
		self.invertedIDXpath = invertedIDXpath
		self.statsPath = statsPath
		self.currItems = 0
		self.maxItems = 10000000
		self.invertedTokensCnt = 0

	def cleanData(self, key, data):
		if key == "reference":
			# Get text only
			data = data.split('\n')
			data = '\n'.join([ i.split('title=')[1].split('|')[0] for i in data if len(i.split('title=')) > 1 ])
		elif key == "link":
			# Get link name
			data = re.sub(r'http\S+', '', data)
			data = '\n'.join([ i.split(']')[0] for i in data.split('\n') ])

		# Tokenization
		data = re.findall(r"[\w']{3,}", data)
		# remove non english words like chinese
		data = [ w for w in data if ord(w[0]) < 122 and ord(w[1]) < 122 and ord(w[2]) < 122 ]
		# Stop words removal
		data = [w for w in data if w not in self.stopwords]
		# Stemming
		data = [ self.stemmer.stem(w) for w in data ]
		return data

	def encodeKeys(self, counts, data):
		data = list(set(data))
		for k in data:
			encoding = str(self.pageCnt)
			for idx, c in enumerate(counts):
				encoding += chr(97 + idx) + str(c[k])
			try:
				self.invertedIdx[k].append(encoding)
			except:
				self.invertedIdx[k] = [encoding]
		self.currItems += len(data)

	def insert(self, data):
		counts = []
		for k in sorted(data.keys()):
			counts.append(Counter(self.cleanData(k, data[k])))
		all_keys = []
		for c in counts:
			all_keys += list(c.keys())
		self.encodeKeys(counts, all_keys)
		# if self.pageCnt % 1000 == 0:
		# 	print(self.pageCnt)

		self.pageCnt += 1
		if self.currItems >= self.maxItems:
			self.saveOne()

	def hashTokens(self, data):
		data = re.findall(r"[\w']{3,}", data)
		for w in data:
			self.originalTokens[w] = 1

	def saveOne(self):
		if self.currItems == 0:
			return
		with open(self.invertedIDXpath + '/Tempfiles/' + str(self.currBlock) + '.txt', 'w') as f:
			all_keys = self.invertedIdx.keys()
			all_keys = list(all_keys)
			all_keys.sort()
			for k in all_keys:
				f.write(k + '-')
				totalLen = len(self.invertedIdx[k]) - 1
				for idx, d in enumerate(self.invertedIdx[k]):
					if idx != totalLen:
						f.write(d + '-')
					else:
						f.write(d + '\n')

		self.invertedIdx = {}
		self.currItems = 0
		self.currBlock += 1

	def saveStats(self):
		with open(self.statsPath, 'w') as f:
			f.write(str(len(self.originalTokens)) + '\n')
			f.write(str(self.invertedTokensCnt) + '\n')

	def getCombined(self, pointers, lists):
		lengths = [ len(l) - 1 for l in lists ]
		toRet = ""
		while not all(k == -1 for k in pointers):
			minW = min([ lists[idx][i].split('a')[0] for idx, i in enumerate(pointers) if i != -1 ])
			for idx, i in enumerate(pointers):
				if i != -1 and lists[idx][i].split('a')[0] == minW:
					toRet += '-' + lists[idx][i]
					if i == lengths[idx]:
						pointers[idx] = -1
					else:
						pointers[idx] += 1
					break
		return toRet

	def mergeFiles(self):
		files = [ f for f in listdir(self.invertedIDXpath + '/Tempfiles/') if isfile(join(self.invertedIDXpath + '/Tempfiles/', f)) ]
		files = [ open(join(self.invertedIDXpath + '/Tempfiles/', f), "r") for f in files ]
		currLines = [ f.readline().strip() for f in files ]

		with open(self.invertedIDXpath + '/finalInvIdx.txt', 'w') as f:
			while not all(not l for l in currLines):
				minW = min([ i.split('-')[0] for i in currLines if i ])
				toWrite = minW
				pointers = [ 0 if f.split('-')[0] == minW else -1 for f in currLines ]
				lists = [ f.split('-')[1:] if f else [] for f in currLines ]
				toWrite += self.getCombined(pointers, lists)
				f.write(toWrite + '\n')
				self.invertedTokensCnt += 1
				currLines = [ f.readline().strip() if f else f for f in files ]

		for f in files:
			f.close()

		if os.path.isdir(self.invertedIDXpath + '/Tempfiles'):
		    shutil.rmtree(self.invertedIDXpath + '/Tempfiles')