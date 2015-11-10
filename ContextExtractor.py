import re
from collections import Counter
import argparse

class Domain:
	def __init__(self, name='Noname'):
		self.name = name
		self.templates = set()
		self.titles = []

	def try_to_add_title(self, url_title):
		for templ in self.templates:
			if re.match(templ, url_title[0]) != None:
				self.titles.append(url_title[1])
				return True
		return False

	def compute_statistics(self):
		stat = Counter()
		for title in self.titles:
			stat.update(set(''.join(c for c in title if c.isalnum() or c.isspace()).split()))
		result = [[word, stat[word]] for word in stat]
		result = sorted(result, reverse=True, key=lambda x: x[1])
		return result


class Category:
	def __init__(self, nm):
		self.name = nm
		self.domains = dict()
		self.all = Domain('all')

	def add_template(self, templ):
		end_of_domain = templ.find(' ')
		if end_of_domain == -1:
			d_name = templ
			templ = '^https?://' + d_name + '.*$'
		else:
			d_name = templ[:end_of_domain]
			templ = templ[end_of_domain + 3:]
			if templ.find('#phrases') != -1:
				templ = templ[: templ.find('#phrases')]
		if not d_name in self.domains:
			self.domains[d_name] = Domain(d_name)
		self.domains[d_name].templates.add(templ)

	def compute_statistics(self):
		return [[dm + " " + str(len(self.domains[dm].titles)), self.domains[dm].compute_statistics()] for dm in self.domains]

	def print_statistics(self):
		print(self.name)
		print("Total in catogory", len(self.all.titles))
		for word in self.all.compute_statistics():
			print("\t\t" + str(word[0]), word[1])
		for dm in self.compute_statistics():
			print("\t" + dm[0])
			for word in dm[1]:
				print("\t\t" + str(word[0]), word[1])

	def add_title(self, url_title):
		flag = False
		for dm in self.domains:
			flag = flag or self.domains[dm].try_to_add_title(url_title)
		if flag:
			self.all.titles.append(url_title[1])


"""Load categories from text file
file structure: 
<category>
<category>
...
<category>

<category>: 
<category_name>
\t<template>
\t<template>
...
\t<template>


Example:
893. Электроника и фото
	avttech.ru
	farpost.ru @ ^https?://(www\.)?farpost\.ru/[a-z0-9_-]+/tech/photo/.*$
894. Аудио- и видеоаппаратура
	all-4u.ru @ ^https?://(www\.)?all-4u\.ru/prod/516/catalog.*$
	all.biz @ ^https?://(www\.)?[a-z_\-]+\.all\.biz/.*bgr1809(\D.*)?$
	aud.abc.ru
"""

cats = []

def LoadCategories(filename):
	for i in open(filename, 'r', encoding="utf-8"):
		if i.startswith('\t'):
			cats[-1].add_template(i[1:-1])
		else:
			cats.append(Category(i[:-1]))

def print_all_categories():
	for c in cats:
		c.print_statistics()

def feedCategories(filename):
	for i in open(filename, 'r', encoding="utf-8"):
		i = i[:-1]
		for c in cats:
			c.add_title(i.split('\t'))

def main():
	parser = argparse.ArgumentParser(description="")
	parser.add_argument('-c', type=str, dest='categories_input')
	parser.add_argument('-u', type=str, dest='urls_input')
	args = parser.parse_args()
	LoadCategories(args.categories_input)
	feedCategories(args.urls_input)
	print_all_categories()

main()