#!/usr/bin/env python

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.preprocessing import MultiLabelBinarizer
import sys
import csv
import numpy

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



# here X and Y are in word form
def vectorize_data(X,Y):
    #vectorize the text documents
    transformer = TfidfVectorizer(analyzer='word',lowercase=True,norm='l2',use_idf=True)
    X_trans = transformer.fit_transform(X)
    #convert the class labels to binary vector
    label_transformer = MultiLabelBinarizer()
    Y_trans = label_transformer.fit_transform(Y)
    return X_trans,Y_trans,label_transformer
    

def learn_one_vs_all(X_train,Y_train,base_classifier):
    ova = OneVsRestClassifier(base_classifier)
    ova.fit(X_train,Y_train)
    #This should return a num_examples * num_classes matrix, with each entry giving distance
    return  ova

def make_class_labels(decision_matrix,topk=5):


    num_classes = len(decision_matrix[0])
    class_indices = range(num_classes)
    all_labels = []
    for example in decision_matrix:
        assert(len(example)==num_classes)
        top_attrs = zip([x for x in example],class_indices);
        top_attrs = sorted(top_attrs,key=lambda(x):x[0],reverse=True)
        top_attrs = top_attrs[:topk]
        example_label_encoding = [0]*num_classes
        for dist,idx in top_attrs:
            example_label_encoding[idx]=1;
        all_labels += [example_label_encoding]

    return all_labels


if __name__=="__main__":

    
    doc_data,doc_labels=read_data(sys.argv[1])
    num_total = len(doc_data)
    f = 0.8
    num_training = int(f*num_total)
    num_test = int((1-f)*num_total)

    # vectorize only the seen class labels, but all of the vocabulary
    Y_train_labels = doc_labels[:num_training]
    Y_test_labels = doc_labels[-num_test:]
    X,Y,label_transformer = vectorize_data(doc_data,Y_train_labels)
    X_train = X[:num_training,:]
    X_test = X[-num_test:,:]
    Y_train = Y
    
    print "Number of training examples", num_training
    print "Number of test examples", num_test



    classifier = LinearSVC(C=0.8,loss='l2') 

    predictor = learn_one_vs_all(X_train,Y_train,classifier)
    raw_predictions = predictor.decision_function(X_test)
    boolean_predictions = make_class_labels(raw_predictions,topk=5)
    label_predictions = label_transformer.inverse_transform(numpy.array(boolean_predictions))

    # rebuild the class mapping 
    for orig,lp in zip(Y_test_labels,label_predictions):
        print orig, "----" ,lp,"\n"
    
    
        


    
    
    



