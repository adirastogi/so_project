import html_tag_remover
import sys
import csv as csv
import os
import fileinput
import nltk
from collections import Counter
from nltk.corpus import stopwords

def main():
    input_file=sys.argv[1]
    distint_words, tags, wordcounts = countWords(input_file)
    print wordcounts

def countWords(input_file):
    wordset = set()
    tagset = set()
    input = open(input_file, 'rb')
    reader = csv.DictReader(input, delimiter=',', quotechar='"')
    wordcounts = {}
    for line in reader:
	tokens = nltk.word_tokenize(line["Title"]) + nltk.word_tokenize(line["Body"])
	frequency = Counter(tokens)
	wordcounts[line["Id"]] = frequency
	wordcounts = dict((k, dict(v)) for k,v in wordcounts.iteritems())	
	wordset = wordset | set(line["Title"].lower().split())
	wordset = wordset | set(line["Body"].lower().split())
	tagset = tagset | set(line["Tags"].lower().split())
#    print wordcounts
    return wordset, tagset, wordcounts 

if __name__ == '__main__':
    main()
