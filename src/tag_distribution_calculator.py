#!/usr/bin/env python
import matplotlib.pyplot as plt
import sys
import csv

def read_data(processed_file):
    doc_train_data = []
    doc_label_data = []
    with open(processed_file,'r') as fhandle:
        reader = csv.DictReader(fhandle);
        for row in reader:
            doc_text = row["Title"] + " " + row["Body"] 
            doc_train_data += [doc_text]
            doc_tags = row["Tags"].split()
            doc_label_data += [doc_tags]
    return doc_train_data,doc_label_data

def calculate_tag_length_dist(doc_label_data):
    tagLen = {}
    for taglist in doc_label_data:
        if len(taglist) not in tagLen : tagLen[len(taglist)] = 1;
        tagLen[len(taglist)] +=1 
    distribution = sorted(tagLen.items(),key=lambda(x):x[0])
    dist_taglen = [x for x,y in distribution]
    dist_tagcount = [y for x,y in distribution]
    

def calculate_most_freq_words(datax):
    wordDict = {}
    for example in datax:
        words = example.strip().split()
        for word in words:
            if word not in wordDict : wordDict[word] = 1
            wordDict[word] +=1

    top_500_words = sorted(wordDict.items(),key=lambda(x):x[1],reverse=True)
    top_500_words = top_500_words[:500]
    for word, count in top_500_words:
        print word,count 
    

if __name__=='__main__':
    datax,datay = read_data(sys.argv[1]);
    calculate_tag_length_dist(datay);
    calculate_most_freq_words(datax)
    
