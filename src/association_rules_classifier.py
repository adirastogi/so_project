#!/usr/bin/env python
import re
import sys
import csv

example_support_thresh = 1
conf_thresh = 0.7
supp_thresh = 0.000002

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

def mine_with_association_rules(X_train,tagDict):
    all_preds = []
    for example in X_train:
        for tag,similar_tags in tagDict:
            if example.count(tag) >= example_support_thresh:
                prediction += tag + tagDict[tag];
                    all_preds += prediction;
    return all_preds;

def build_tag_dict(filename):
    tagDict = {}
    with open(filename,'r') as fhandle:
        for line in fhandle:
            info = re.split('[ ,()\n]', line)
            tag, relatedTag, supp, conf = info[2], info[0], float(info[4]), float(info[6])
            if conf >= conf_thresh and supp >= supp_thresh:
                if tag not in tagDict : tagDict[tag]=[]
                tagDict[tag] += [relatedTag];
    return tagDict;
        

if __name__=="__main__":
   
    doc_train_data, doc_train_labels = read_data(sys.argv[1])
    doc_test_data, doc_test_labels = read_data(sys.argv[2])
    tagDict = build_tag_dict(sys.argv[3])
    all_pred = mine_with_association_rules(doc_train_data,tagDict)

    print "The predictions are"
    for pred,orig in zip(all_pred,doc_test_labels):
        print orig,"---",pred

    #calculate the mean-fscore
    print "The mean f-score is ", mean_f1.mean_f1(doc_test_labels,all_pred)
    
 
