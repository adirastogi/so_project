import html_tag_remover
import sys
import csv as csv
import os
import fileinput
import nltk
import string
from nltk.corpus import stopwords

def main():
    filename = sys.argv[1]
    lazy_stopword_filter(filename)

def lazy_stopword_filter(filename):
    exclude_punctuation = set(['[', ']', '{', '}', '(', ')', ',','!','?',';',':','<', '>'])
    stop_set = set(stopwords.words('english'))
    with open("../resources/stopwords.txt", 'r') as f:
	stop_set = stop_set | set((l.strip() for l in f.readlines()))
    outfile = sys.argv[2]
    text = open(filename, 'rb')
    reader = csv.DictReader(text, delimiter=',', quotechar='"')
    target = open(outfile, 'wb')
    fieldnames=['Id', 'Title', 'Body', 'Tags']
    writer = csv.DictWriter(target, fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(dict((fn, fn) for fn in fieldnames))
    for line in reader:
        # remove multiple spaces from all columns 
        for k,v in line.items():
            line[k] = ' '.join(v.split())
	str_to_write_title = ""
	for word in line["Title"].split():
	    word = ''.join(ch for ch in word if ch not in exclude_punctuation)
	    if word.lower() not in stopwords.words('english'):
		str_to_write_title = str_to_write_title + " " + word
	#print(str_to_write_title)	
	str_to_write_body = "" 
	
	body = html_tag_remover.cleanup_html(line["Body"])
        for word in body.split(): # simple tokenization
	    word = ''.join(ch for ch in word if ch not in exclude_punctuation)
            if word.lower() not in stop_set:
	        str_to_write_body = str_to_write_body + " " + word
	#print(str_to_write_body)

	writer.writerow({'Id': line["Id"], 'Title':str_to_write_title, 'Body': str_to_write_body, 'Tags':line["Tags"]})	
if __name__ == '__main__':
    main()

