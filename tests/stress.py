#!/usr/bin/env python
# coding: utf-8
import optparse
import urllib
import random

text = u"Мальчик, который выжил."
alpha = u'абвгдежзиклмнопрстуфхцчшъыьэюя, '

def mutate(text):
	for errno in xrange(abs(int(random.gauss(0, 3)))):
		place = random.randint(0, len(text) - 1)
		if random.choice('id') == 'i':
			text = text[:place] + random.choice(alpha) + text[place:]
		else:
			text = text[:place] + text[place+1:]
	return text

def fetch(url):
	fd = urllib.urlopen(url)
	reply = fd.read()
	fd.close()
	return reply

def attempt():
	fetch(options.url + "/zhivoeslovo/")
	query = urllib.urlencode(dict(dict_text=mutate(text).encode('utf-8')))
	fetch(options.url + "/zhivoeslovo/ajax/results/?" + query)

def main():
	for n in range(options.count):
		if n % 100 == 0:
			print n
		attempt()

if __name__ == "__main__":
	parser = optparse.OptionParser()
	parser.add_option("-u", "--url", help="Where to connect")
	parser.add_option("-n", "--count", type=int, help="How many times")
	options, args = parser.parse_args()
	main()
