#!/usr/bin/env python

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import LogisticRegression
import sys
import csv
import numpy
from scipy.sparse import csr_matrix
from scipy.sparse import csc_matrix
from fplist import create_fplist
import heapq
import mean_f1
import itertools

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

# takes Y in the list of labels format and builds a scipy sparse matrix out of it
def build_sparse_class_matrix(Y_list):
 
    #get the distinct classes and assign them a fixed ordering 
    indices = []
    all_y = []
    indptr = []
    data = []
    for label_list in Y_list:
        all_y += label_list
    uniq_labels = sorted(list(set(all_y)))
    num_cols = len(uniq_labels)
    num_rows = len(Y_list)
    count = 0;
    for y in Y_list:
        indptr += [count]
        for label in y:
            idx = uniq_labels.index(label)
            indices += [idx]
            count +=1
            data += [1]
    indptr += [count]

    data = numpy.array(data)
    indptr= numpy.array(indptr)
    indices = numpy.array(indices)
    csr =  csr_matrix((data,indices,indptr),shape=(num_rows,num_cols))
    return csr,uniq_labels


# here X and Y are in word form
def vectorize_data(X,Y):
    #vectorize the text documents
    transformer = TfidfVectorizer(analyzer='word',lowercase=True,norm='l2',use_idf=True)
    X_trans = transformer.fit_transform(X)
    #convert the class labels to binary vector
    # the Y matrix will be too big to fit in memory so convert it to compressed sparse row form 
    #uniq_label_mapping = MultiLabel/Binarizer()
    #Y_trans = uniq_label_mapping.fit_transform(Y)
    
    Y_trans,uniq_label_mapping = build_sparse_class_matrix(Y)
    return X_trans,Y_trans,uniq_label_mapping
    

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


# convert the list of tags into a tuple and lookup its index in the list. returns the 
# frequent pattern sets encoded as indices
def convert_y_to_label_indices(Y_train,fp_set_list):
   
    #print fp_set_list

        
    class_label_indices = [] 
    #print len(Y_train)
    for example in Y_train:
        example_t = tuple(sorted(example)); 

        #check for all subsets , set the feature for the max len subset 
        l = len(example_t)
        maxlen = 0;
        maxfound = False;
        foundindex = -1
        idx = -1
        for i in range(1,l+1):
            subset_list = list(itertools.combinations(example_t,i))
            for subset in subset_list:
                subset_t = tuple(sorted(list(subset)))
                if subset_t in fp_set_list: 
                    if i > maxlen: 
                        maxlen = i; 
                        maxfound = True
                        foundindex = fp_set_list.index(subset_t)
                        break;
        idx = foundindex
        '''
            if maxfound:
                idx = foundindex
                break;
            else: continue 
        '''
        ###### idx should have been found
        if idx==-1: print "Not found", example_t
        #print example_t
        class_label_indices += [idx]


    new_fp_set_list = []
    new_class_label_indices = []
    new_idx = -1;
    for i in range(len(class_label_indices)):
        idx = class_label_indices[i]
        if fp_set_list[idx] not in new_fp_set_list:
            new_fp_set_list += [fp_set_list[idx]]
            new_idx +=1;
            class_label_indices[i] = new_idx;
        else:
            class_label_indices[i] = new_fp_set_list.index(fp_set_list[idx]) 
    

    print max(class_label_indices)
    print len(new_fp_set_list)

    for s,k in zip(fp_set_list,range(len(fp_set_list))):
        print k, " ", s;

    print "-"*100

    assert(len(class_label_indices)==len(Y_train))
   
    # print the mapping
    for example,idx in zip(Y_train,class_label_indices):
        print idx , " ", example

    return class_label_indices,new_fp_set_list

def convert_label_indices_to_y(Y_label_indices,fp_set_list):
    
    class_label_sets = []
    for idx in Y_label_indices:
        label_set = fp_set_list[idx]
        class_label_sets += [label_set]
    
    return class_label_sets
    
# builds a sparse multiclass matrix from 1-d array of class indices.
def build_sparse_multiclass_matrix(Y_index_list,fp_set_list):


    data = []
    indptr = []
    indices  = [] 
    num_classes = len(fp_set_list)
    num_examples  = len(Y_index_list)
    indices = Y_index_list
    data = [1]*num_examples
    indptr = range(0,num_examples+1)

    data = numpy.array(data)
    indptr= numpy.array(indptr)
    indices = numpy.array(indices)

    csr_mat = csr_matrix((data,indices,indptr),shape=(num_examples,num_classes))
    #print csr_mat.todense()
    return csr_mat

# takes in the Y_train in raw format
def run_multiclass(X_train,X_test,Y_train_labels,fp_set_list):
    # convert to label indices
    Y_index_list,new_fp_set_list = convert_y_to_label_indices(Y_train_labels,fp_set_list)
    # convert it to a sparse matrix
    csr_mat = build_sparse_multiclass_matrix(Y_index_list,new_fp_set_list)
    class_label_preds = train_custom_one_vs_all(X_train,X_test,csr_mat,topk=1)
    label_predictions = []
    #label here wil be a list of single element and label_set is a set 
    for label in class_label_preds:
        idx = label[0]
        label_set = new_fp_set_list[idx]
        label_predictions += [label_set]
    
    return label_predictions 

# takes in the Y_train converted to sparse matrix 
def run_multilabel(X_train,X_test,Y_train,uniq_label_mapping):
    class_label_preds = train_custom_one_vs_all(X_train,X_test,Y_train,topk=3)
    label_predictions = []
    for pred in class_label_preds:   
        t = [uniq_label_mapping[i] for i in pred]
        label_predictions += [t]
    return label_predictions

# since the scipy one vs all uses dense y arrays, it runs out of memory,
# to fix that, i need to train one vs all for one class at a time, just like
# one vs all does, store the n learnt classifiers and then for any new example
# predict the distance form each classifier
# Y_train is in csr format, for column splicign convert to csc
def train_custom_one_vs_all(X_train,X_test,Y_train,topk):

    #convert matrix to row for efficient splicing
    Y_train = Y_train.tocsc()
    tag_classifiers = []
    num_training,numclasses = Y_train.shape
    num_test_examples = X_test.shape[0]


    # hold a vector mxk, containing top k prediction classes for each example, maintain m heaps for that
    num_examples = X_test.shape[0]
    num_classes = len(tag_classifiers)
    topk_class_distances = []
    for i in xrange(num_examples):
        heap = []
        topk_class_distances += [heap]
    

    for j in xrange(numclasses):
        # train on each class label for all the training examples
        y = numpy.ravel(Y_train.getcol(j).todense());

        clf = LogisticRegression(penalty='l2',dual=False,tol=0.0001,C=0.8,fit_intercept=True,intercept_scaling=1)
    
        clf.fit(X_train,y);
        print "Trained for class",j
        # get the decision for all test examples
        decision = clf.decision_function(X_test)
        # for each test example add its decision value to the heap of top k decision values
        for i in xrange(num_test_examples):
            h = topk_class_distances[i]
            if len(h) < topk: heapq.heappush(h,(decision[i],j))
            else:             heapq.heappushpop(h,(decision[i],j))
        print "Predicted for class",j

    #clean the decision values and store the class labels
    class_label_indices = []
    for i in xrange(num_examples):
        topk_labels = [label for dist,label in topk_class_distances[i]]
        class_label_indices += [topk_labels]

    return class_label_indices
     
        
def class_inverse_transform(boolean_mat,label_mapping):

    #boolean_mat is a sparse matrix , will cause memory problems
    all_labels = []
    for row in boolean_mat:
        labels = [];
        for colidx in xrange(len(row)):
            if row[colidx]==1:
                labels += [label_mapping[colidx]]
        all_labels += [labels]

    return all_labels
                    
    '''   
    row_idx,col_idx = boolean_mat.nonzero()
    row_idx = row_idx.tolist()
    col_idx = col_idx.tolist()

    for r,c in zip(row_idx,col_idx):
        tagname = label_mapping[c]
        if r not in all_labels: all_labels[r] = []
        all_labels[r] += [tagname]

    key_label_map = sorted(all_labels.items(),key=lambda(x):x[0])
    label_list = [l for k,l in key_label_map]    
    return label_list

    '''
            

if __name__=="__main__":

    
    doc_data,doc_labels=read_data(sys.argv[1])
    num_total = len(doc_data)
    f = float(sys.argv[2])
    num_training = int(f*num_total)
    num_test = int((1-f)*num_total)

    # vectorize only the seen class labels, but all of the vocabulary
    Y_train_labels = doc_labels[:num_training]
    Y_test_labels = doc_labels[-num_test:]
    X,Y,uniq_label_mapping = vectorize_data(doc_data,Y_train_labels)
    X_train = X[:num_training,:]
    X_test = X[-num_test:,:]
    Y_train = Y
    
    print "Number of training examples", num_training
    print "Number of test examples", num_test

    true_labels = [list(item) for item in Y_test_labels]

    '''
    predictor = learn_one_vs_all(X_train,Y_train,classifier)
    raw_predictions = predictor.decision_function(X_test)
    boolean_predictions = make_class_labels(raw_predictions,topk=3)
    label_predictions = class_inverse_transform(boolean_predictions,uniq_label_mapping)
    #label_predictions = uniq_label_mapping.inverse_transform(numpy.array(boolean_predictions))

    label_predictions = [list(item) for item in label_predictions]
    assert(len(label_predictions)==len(true_labels))

    '''
    fp_set_list = create_fplist(sys.argv[3])

    '''
    fp_set_list = [
        ('file-upload', 'image-processing', 'mime-types', 'php', 'upload'),
        ('firefox',),
        ('c#','encoding','url'),
        ('machine-learning', 'matlab', 'r') 
    ]
    '''

    label_predictions =  run_multiclass(X_train,X_test,Y_train_labels,fp_set_list)

    ''' 
    #new custom classifier code, will give n tag classifiers. sparsified
    class_label_preds = train_custom_one_vs_all(X_train,X_test,Y_train,topk=3)
    label_predictions = []
    for pred in class_label_preds:   
        t = [uniq_label_mapping[i] for i in pred]
        label_predictions += [t]
    '''

    # print the predictions mapping 
    for orig,lp in zip(true_labels,label_predictions):
            print orig, "----" ,lp,"\n"
       
 
    #calculate the mean-fscore
    print "The mean f-score is ", mean_f1.mean_f1(true_labels,label_predictions)
        
        


    
    
    



