import re
from nltk.stem import PorterStemmer
from collections import Counter

class DataHolder():
	def __init__(self):
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
		self.invertedIdx = {}

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
		for k in data:
			encoding = str(self.pageCnt)
			for idx, c in enumerate(counts):
				encoding += chr(97 + idx) + str(c[k])
			try:
				self.invertedIdx[k].append(encoding)
			except:
				self.invertedIdx[k] = [encoding]

	def insert(self, data):
		counts = []
		for k in data.keys():
			counts.append(Counter(self.cleanData(k, data[k])))
		all_keys = []
		for c in counts:
			all_keys += list(c.keys())
		self.encodeKeys(counts, all_keys)
		if self.pageCnt % 1000 == 0:
			print(self.pageCnt)
		self.pageCnt += 1

	def save(self, path1, path2):
		with open(path1, 'w') as f:
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
