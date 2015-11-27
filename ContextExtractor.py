import re
from collections import Counter
import argparse

class Domain:
	def __init__(self, name='Noname'):
		self.name = name
		self.templates = set()
		self.titles = []

	def compute_statistics(self, stopwords=[], minlen=0):
		stat = Counter()
		for title in self.titles:
			stat.update(set(filter(lambda x: not x in stopwords and len(x) >= minlen, ''.join(c for c in title if c.isalnum() or c.isspace()).lower().split())))
		result = [[word, stat[word]] for word in stat]
		result = sorted(result, reverse=True, key=lambda x: x[1])
		return result


class Category:
	def __init__(self, nm):
		self.name = nm
		self.domains = dict()
		self.all = Domain('all')
		self.stopwords = []

	def compute_statistics(self, stopwords=[], minlen=0):
		return [[dm, len(self.domains[dm].titles), self.domains[dm].compute_statistics(stopwords, minlen)] for dm in self.domains]

	def print_statistics(self, urlcntlim=0, wordcntlim=0, stopwords=[], minlen=0):
		print(self.name)
		print("Total in catogory", len(self.all.titles))
		for word in self.all.compute_statistics(stopwords, minlen):
			if word[1] >= wordcntlim:
				print("\t\t" + str(word[0]), word[1])
		for dm in self.compute_statistics(stopwords, minlen):
			if dm[1] >= urlcntlim:
				print("\t" + dm[0] + ' ' + str(dm[1]))
				for word in dm[2]:
					if word[1] < wordcntlim:
						break
					print("\t\t" + str(word[0]), word[1])

	def add_title(self, d_name, title):
		if not d_name in self.domains:
			self.domains[d_name] = Domain(d_name)
		self.domains[d_name].titles.append(title)
		self.all.titles.append(title)

catdict = dict()

def add_urls_categ_title(url_categ_title):
	url, categ, title = url_categ_title.split('\t')
	dmn = url
	if dmn.startswith('http://'):
		dmn = dmn[7:]
	elif dmn.startswith('https://'):
		dmn = dmn[8:]
	first_slash = dmn.find('/')
	if first_slash != -1:
		dmn = dmn[:first_slash]
	if not categ in catdict:
		catdict[categ] = Category(categ)
	catdict[categ].add_title(dmn, title)


def print_statistics(urlcntlim=0, wordcntlim=0, stopwords=[], minlen=0):
	for c in sorted(catdict.keys()):
		catdict[c].print_statistics(urlcntlim, wordcntlim, stopwords, minlen)

def main():
	parser = argparse.ArgumentParser(description="")
	parser.add_argument('-i', type=str, dest='input', help='Input file from admining', required=True)
	parser.add_argument('-s', type=str, dest='stwords', help='File with stop words')
	parser.add_argument('-ul', type=int, dest='urlcntlim', help='Minimum limit of urls for each domain')
	parser.add_argument('-wl', type=int, dest='wordcntlim', help='Minimum limit of words for each domain')
	parser.add_argument('-ml', type=int, dest='minlen', help='Minimal length of word')
	args = parser.parse_args()
	for i in open(args.input, 'r', encoding="utf-8"):
		add_urls_categ_title(i[:-1])
	stw = []
	if args.stwords != None:
		stw = [i for i in open(args.stwords, 'r', encoding="utf-8").read().lower().split('\n')]
	urlcntlim = 0 if args.urlcntlim == None else args.urlcntlim
	wordcntlim = 0 if args.wordcntlim == None else args.wordcntlim
	minlen = 0 if args.minlen == None else args.minlen
	print_statistics(urlcntlim, wordcntlim, stw, minlen)

main()
