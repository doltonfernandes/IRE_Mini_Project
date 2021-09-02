import sys
from dataHolder import DataHolder
import json

invertedIdxPath = sys.argv[1] + '/finalInvIdx.txt'
query = sys.argv[2]

invertedIdx = {}
with open(invertedIdxPath, 'r') as f:
	data = f.read()
data = data.split('\n')[:-1]

for t in data:
	invertedIdx[t.split('-')[0]] = t.split('-')[1:]

holder = DataHolder('', '')

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
if ':' not in query:
	query = holder.cleanData('', query.lower())
	query = list(set(query))

	for q in query:
		ans[q] = emptyQuery
		for k in ans[q].keys():
			ans[q][k] = getDocIds(q, mapping[k])
else:
	queryFormatted = {}
	for k in emptyQuery.keys():
		if k[:1] + ':' in query:
			text = query.split(k[:1] + ':')[1]
			if ':' in text:
				text = text.split(':')[0][:-1]
			text = holder.cleanData('', text.lower())
			for w in text:
				try:
					queryFormatted[w].append(k)
				except:
					queryFormatted[w] = [k]

	for w in queryFormatted.keys():
		ans[w] = emptyQuery
		for q in queryFormatted[w]:
			ans[w][q] = getDocIds(w, mapping[q])

print(json.dumps(ans, indent=4))