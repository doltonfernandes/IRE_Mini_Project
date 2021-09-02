import sys
import json
import re
from nltk.stem import PorterStemmer

invertedIdxPath = sys.argv[1] + '/finalInvIdx.txt'
query = sys.argv[2]

invertedIdx = {}
with open(invertedIdxPath, 'r') as f:
	data = f.read()
data = data.split('\n')[:-1]

for t in data:
	invertedIdx[t.split('-')[0]] = t.split('-')[1:]

emptyQuery = {
	"title": [],
	"body": [],
	"infobox": [],
	"categories": [],
	"references": [],
	"links": [],
}

mapping = {}
for idx, i in enumerate(sorted(emptyQuery.keys())):
	mapping[i] = chr(97 + idx)

def getDocIds(word, c):
	docIds = []
	if c == 'f':
		for d in invertedIdx[word]:
			if int(d.split('f')[1]) > 0:
				docIds.append(int(d.split('a')[0]))
		return docIds

	for d in invertedIdx[word]:
		if int(d.split(c)[1].split(chr(ord(c) + 1))[0]) > 0:
			docIds.append(int(d.split('a')[0]))

	return docIds

ans = {}
stemmer = PorterStemmer()
if ':' not in query:
	query = re.findall(r"[\w']{1,}", query)
	query = list(set(query))

	for q in query:
		ans[q] = emptyQuery
		for k in ans[q].keys():
			try:
				ans[q][k] = getDocIds(stemmer.stem(q.lower()), mapping[k])
			except:
				pass
else:
	queryFormatted = {}
	for k in emptyQuery.keys():
		if k[:1] + ':' in query:
			text = query.split(k[:1] + ':')[1]
			if ':' in text:
				text = text.split(':')[0][:-1]
			text = re.findall(r"[\w']{1,}", text)
			text = list(set(text))
			for w in text:
				try:
					queryFormatted[w].append(k)
				except:
					queryFormatted[w] = [k]

	for w in queryFormatted.keys():
		ans[w] = emptyQuery
		for q in queryFormatted[w]:
			try:
				ans[w][q] = getDocIds(stemmer.stem(w.lower()), mapping[q])
			except:
				pass

print(json.dumps(ans, indent=4))