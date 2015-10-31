#!/usr/bin/env python
# coding: utf-8
import optparse
import random

alpha = u'абвгдежзиклмнопрстуфхцчшъыьэюя, '

def mutate(text):
	for errno in range(abs(int(random.gauss(options.mean, options.dispersion)))):
		place = random.randint(0, len(text) - 1)
		if random.choice('id') == 'i':
			text = text[:place] + random.choice(alpha) + text[place:]
		else:
			text = text[:place] + text[place+1:]
	return text

def main():
  for line in args:
    for n in range(options.count):
      print(mutate(line))

if __name__ == "__main__":
  parser = optparse.OptionParser()
  parser.add_option("-m", "--mean", type=float, default=0, help="Gauss mean N errors")
  parser.add_option("-d", "--dispersion", type=float, default=3, help="Gauss dispersion of N errors")
  parser.add_option("-n", "--count", type=int, help="Amount of mutations to produce")
  options, args = parser.parse_args()
  main()
