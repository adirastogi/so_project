import itertools;
import sys;
import os;
import math;
import os.path;
import errno;


'''Structure of a node :
(
    <node_label>,
    [<node_count_after_tree_build>],
    {dict of ref_to_child_nodes},
    <ref_to_parent>
)'''

'''Structure of data :
    list of transactions where each transaction is a pair of [<frequency_of_itemset>,<item_lables_as_a_list>,]
'''
'''Sructure of frequent itemset list
    list of pairs where each pair is [<item_lables_as_a_list>,<frequency_of_itemset>]
'''

def read_transaction_file(filename):
    '''This function reads the transaction file specified by filename
    and returns the read data as a list of list of items'''
    with open(filename,'r') as file:
        data = [ [1,sorted(line.split())] for line in file];
    return data;  

#======================== FP-tree implementation ====================#
def node_label(node):
    '''returns the label of the node'''
    return node[0];

def node_children(node):
    '''returns a dict containing the nodes that are node's children'''
    return node[2];

def increment_count(node,value):
    '''Increments the count of the node'''
    node[1][0] += value;

def node_count(node):
    '''returns the count stored at a node'''
    return node[1][0];

def node_parent(node):
    '''return the node parent'''
    return node[3];

def print_fptree(root):
    '''prints the fptree rooted at root'''
    print node_label(root),node_count(root);
    print "children of ",node_label(root);
    for child in node_children(root).values():
        print_fptree(child);
    print "end children of ",node_label(root);

def node_first_child(node):
    '''returns the first child of a node if dict size is 1 None otherwise'''
    if len(node[2])==1: return node[2].values()[0];
    else : return None

def calculate_support(data,min_sup,total_trans):
    '''Data here is a list of list of items and the frequency of that itemset'''
    support_count = {};
    for transaction in data:
        for item in transaction[1]:
            if item not in support_count:
                support_count[item] = transaction[0];
            else:
                support_count[item] += transaction[0];
    # filter the list and the data to remove items that do not satisfy the minimum support count
    low_items = [k for k,v in support_count.items() if v<min_sup*total_trans];
    for transaction in data:
        transaction[1] = [item for item in transaction[1] if item not in low_items];
    support_count = dict( (k,v) for (k,v) in support_count.items() if k not in low_items);
    return support_count;        

def build_fptree(data,min_sup,total_trans):
    '''This function takes the transaction data rep as a list of list of items and 
    returns the FPtree out of it '''
    # the root node is a dummy item with no description and 0 count 
    tree_root  = (None,[0],{},None); 
    # first build the support data for each item
    data_support = calculate_support(data,min_sup,total_trans);
    # the item header table for each item. For each item key this is a dictionary that stores the count, 
    # and the list of item nodes for that item in the tree. Initializing the count and the list to empty 
    item_table = {};
    for item,count in data_support.items():
        item_table[item] = (count,[]);
    # for each transaction in the data
    for trans in data:
        #look at the items in descending order of their count values.
        sorted_items = sorted(trans[1],key=lambda item: data_support[item], reverse = True);
        root = tree_root;
        # search for the items starting from the root, which is a null node.
        for item in sorted_items: 
            # if the item already matches a node in the tree, increment your count.
            root_children = node_children(root);
            if item in root_children:
                item_node = root_children[item];
                increment_count(item_node,trans[0]);
            # otherwise, start a new branch from this node
            else:
                item_node = (item,[trans[0]],{},root);
                root_children[item] = item_node;
                item_table[item][1].append(item_node);
            # for the subsequent nodes, the tree will be grown from this node
            root = item_node;    
    return (tree_root,item_table);

def mine_fptree(root,item_table,min_sup,total_trans):
    '''This function mines the fptree and returns a list of frequent itemset tuples
    and their associated counts '''

    freq_itemsets = [];
    # check if the tree is straight.
    trav = root;
    while len(node_children(trav))==1:
        trav = node_first_child(trav);        
    if len(node_children(trav))==0 and trav is not root:
        #yes tree is straight, return all combinations.
        trav = node_first_child(root);
        node_label_list = [];
        # create a list out of the tree
        while trav :
            node_label_list.append(node_label(trav));
            trav = node_first_child(trav);
        # generate all combinations of the list and create frequent itemsets
        for r in xrange(1,len(node_label_list)+1): 
            combins = itertools.combinations(node_label_list,r);
            for comb in combins:
                freqs = [item_table[i][0] for i in comb];
                min_freq = min(freqs);
                freq_itemsets.append([list(comb),min_freq]);
                
    elif len(node_children(root))>0:
        #the tree is non-empty and branched 
        # get the list of items in ascending count 
        ordered_items = sorted(item_table.items(), key=lambda (k,v): v[0]);   
        for item_label,(total_item_count,item_thread) in ordered_items:
            # for each item_label
            data = [];
            itemset_table = {};
            # disregard the item_label if its total support is less than threshold
            if total_item_count < min_sup*total_trans: continue;
            for item_node in item_thread:
                # build the new transaction table data, where each transaction is now a set of items
                itemset = [];
                trav = node_parent(item_node);
                while trav is not root:
                    itemset.append(node_label(trav));
                    trav = node_parent(trav);
                if len(itemset) >0:
                    #append only non-empty itemsets
                    data.append([node_count(item_node),itemset]);
            # now the data is conditioned on the item_label, mine frequent itemsets on this data
            (new_root,new_item_table) = build_fptree(data,min_sup,total_trans);
            new_freq_itemsets = mine_fptree(new_root,new_item_table,min_sup,total_trans);
            #append this to the recursively obtained frequent itemsets
            for (item_list, min_freq) in new_freq_itemsets:
                item_list.append(item_label);
                min_freq = min(min_freq,total_item_count);
                freq_itemsets.append([item_list,min_freq]);
            # add self to make 1 frequent itemset
            freq_itemsets.append([[node_label(item_node)],total_item_count])
            
    return freq_itemsets;


def min_fpgrowth(data,min_sup,total_trans):
    (root,item_table) = build_fptree(data,min_sup,total_trans);
    freq_itemsets = mine_fptree(root,item_table,min_sup,total_trans);
    return freq_itemsets;

##===================== A-Prioir Implementation ===================#

def has_all_freq_subitem(cand_item,cand_k_items,min_sup,total_trans):
    '''This checks whether all k-item subsets of a given cand_item are frequent'''
    k = len(cand_k_items.keys()[0]);
    combs = itertools.combinations(cand_item,k)
    assert(len(cand_item)==k+1);
    for comb in combs:
        if comb not in cand_k_items or cand_k_items[comb]<min_sup*total_trans:
            return False;
    return True;
    
def generate_next_cands(cand_k_items,min_sup,total_trans):
    '''This generates the candidate k+1 itemset from candidate k-itemset'''
    # the data in each of the itemsets is lexicographically sorted, each itemset is represented as a tuple
    cand_k_plus_itemlist = [];
    for itemset1 in cand_k_items.keys():
        for itemset2 in cand_k_items.keys():
            if itemset1[:-1]==itemset2[:-1] and itemset1[-1]<itemset2[-1]:
                orig = list(itemset1[:-1]);
                cand_item = orig+ [itemset1[-1]] + [itemset2[-1]];
                # prune candidate if all its subset itemsets are not frequent
                if has_all_freq_subitem(cand_item,cand_k_items,min_sup,total_trans):
                    cand_k_plus_itemlist.append(cand_item);
    return cand_k_plus_itemlist;

def itemset_freq(itemset,data):
    '''returns the frequency with with the given itemset (rep as tuple) appears in data'''
    count = 0;
    itemset_len = len(itemset);
    for trans in data:
        if itemset_len-trans[0]>1: continue;
        itemlist = trans[1];
        # assuming both itemlist and itemset are sorted.
        count_same = len([val for val in itemset if val in itemlist]);
        if count_same==itemset_len:
            count+=1;
            trans[0]=itemset_len;
    return count;
        

def mine_apriori(data,min_sup,total_tran):
    '''This function mines the data in data (rep as a list) that satisfies the minsup (0-1) using apriori algo
    data is a list of transactions where each transaction is of 
    [[smallest_size_itemset_so_far_in_trans],[sorted list of items]]'''
    # build the singleton-itemset list
    map = {};
    freq_itemsets=[];
    for trans in data:
        for item in trans[1]:
            if (item,) not in map: map[(item,)]=1;
            else: map[(item,)]+=1;
    next_itemset_list=map.keys();
    
    while next_itemset_list:
        cand_itemset = {}; # the itemset for this iteration (produced with the next_itemset_list)
        # prune itemsets that are not frequent in the database
        for itemset in next_itemset_list:
            ifreq = itemset_freq(itemset,data);
            if ifreq >= min_sup*total_trans:
                cand_itemset[tuple(itemset)]=ifreq;
        # the itemset so built is final, append it to the final list.
        if cand_itemset:
            freq_itemsets += (cand_itemset.items());
        next_itemset_list = generate_next_cands(cand_itemset, min_sup, total_trans);
        
    return freq_itemsets;


def issubset(s1,s2):
    if ((set(s1) & set(s2) )== set(s1)):
        return True;
    else:
        return False;

def find_closed_maximal_freq_itemsets(freq_itemsets,min_supp,total_trans):
    '''This function extracts the closed frequent itemsets from the given 
    frequent itemsets'''
    #now find itemsets that are closed, sort the itemsets based on length first
    open_itemsets = [];
    non_maximal_itemsets = [];
    freq_itemsets = sorted(freq_itemsets,key=lambda(itemset,supp):len(itemset));
    num_itemsets = len(freq_itemsets);
    for c in xrange(num_itemsets):
        for p in xrange(c+1,num_itemsets):
            child_supp = freq_itemsets[c][1];
            parent_supp = freq_itemsets[p][1];
            if issubset(freq_itemsets[c][0],freq_itemsets[p][0]):
                if parent_supp > min_supp*total_trans:
                    #atleast one superset is frequent, so this subset is not maximal
                    non_maximal_itemsets.append(tuple(freq_itemsets[c][0]));
                if child_supp == parent_supp:
                    open_itemsets.append(tuple(freq_itemsets[c][0]));      
                    break;
    open_itemsets = set(open_itemsets);
    non_maximal_itemsets = set(non_maximal_itemsets);
    closed_itemsets = [(itemset,supp) for (itemset,supp) in freq_itemsets if tuple(itemset) not in open_itemsets];
    maximal_itemsets = [(itemset,supp) for (itemset,supp) in freq_itemsets if tuple(itemset) not in non_maximal_itemsets];
    return closed_itemsets,maximal_itemsets; 
     

fileidx = lambda(filename): os.path.basename(filename).split('-')[1][0]

def print_freq_itemsets(freq_itemsets,filename,vocabulary):
    file = open(filename,'w');
    freq_itemsets = sorted(freq_itemsets,key=lambda (iset,msp): msp ,reverse=True);
    for (itemset,min_sup) in freq_itemsets:
        itemset = list(itemset);
        #convert from numbers to words and sort
        words = [vocabulary[int(i)] if vocabulary is not None else i for i in itemset];
        words.sort();
        print >>file, ("%f "+ " %s"*len(itemset))%tuple([min_sup]+words);
    file.close();
    print "Wrote file ",filename;
    return;

def calculate_purity_support_ranking(freq_patt_filenames,min_supp,D,vocabulary):
    '''This function reads the pattern files for each topic
    in the pattern_file_dir directory and creates the purity files
    for each topic'''

    try:    os.mkdir('./purity');
    except OSError as e:
        if e.errno==errno.EEXIST : pass;
    
    data= [];
    for filename in freq_patt_filenames:
        file_data={};
        with open(filename,'r') as f:
            for line in f:
                tokens=line.split();
                file_data[tuple(tokens[1:])]=float(tokens[0]);
        data.append(file_data);
   
    for i in xrange(len(data)):
        purity={};
        for pattern in data[i].keys():
           #cacluate the purity only for patterns that are frequent in data[i] and data[j], i.e f(j,p)=0 
           freq_i = data[i][pattern]*D[i][i];
           
           supports = [float(freq_i+(data[j][pattern]*D[j][j]))/D[i][j] if pattern in data[j] else float(freq_i+0)/D[i][j] for j in xrange(len(data)) if j!=i];
           max_term = max(supports);
           purity[pattern] = math.log(freq_i/D[i][i]) - math.log(max_term);
           
           #purity has been calculated, now calculate ranking by multiplying purity and support. for printing, print
           #purity but sort the results by ranking measure.
        ranking_list  = [];
        for pattern in purity:
            measure = purity[pattern]*data[i][pattern];
            ranking_list.append((pattern,purity[pattern],measure));
               
        #sort the list based on descing order of measure.
        ranking_list.sort(key=lambda(pat,pur,mes):mes,reverse=True);
        ranking_list = [(pattern,pur) for (pattern,pur,meas) in ranking_list];
    
        print_freq_itemsets(ranking_list, './purity/'+'purity-'+str(fileidx(freq_patt_filenames[i]))+'.txt',None);

def rank_topic(metrics,numdocs):
    '''Calculates and returns the ranks of all the pattern in a given topic using
    purity,max,closed and frequent values'''
    pattern_ranking = {};
    #look at only the frequent patterns
    for pattern,supp in metrics['pattern'].items():
        #calculate coverage
        cov = supp;
        #calculate purity
        pur = metrics['purity'][pattern];
        #calculate phraseness
        tvals = [ math.log(metrics['pattern'][(word,)]) for word in pattern if (word,) in metrics['pattern']];
        phr = math.log(cov) - sum(tvals);
        # a pattern is considered complete only if it is closed or maximal closed.
        if pattern in metrics['max']:
            comp=1;
        elif pattern in metrics['closed']:
            comp=0.5;
        else:
            comp=0.1;
        rank = comp*cov*(0.5*pur+0.5*phr);
        pattern_ranking[pattern]=rank;
    return pattern_ranking;
                    
                    
def calculate_new_ranking(topicfiledir,D):
    '''This function reads the pattern and associated metrics from the
    generated files and prints the final ranking that combines all the information
    from the pattern,closed,max and purity files'''
    # calculate the number of files to process
    numtopics = 0;
    for filename in os.listdir(topicfiledir):
         if os.path.isfile(topicfiledir+'/'+filename) and filename.find('topic-')==0:
             numtopics+=1;
             
    #make the directory for storing the results from the new ranking .
    try:    os.mkdir('./bonus_ranking');
    except OSError as e:
        if e.errno==errno.EEXIST : pass;

    #now calcualte the ranking for each file
    dirs = [('patterns','pattern'),('closed','closed'),('max','max'),('purity','purity')];
    for file_idx in xrange(numtopics):
        metrics = {};
        for dirname,filename in dirs:
            dict = {};
            with open(dirname+'/'+filename+'-'+str(file_idx)+'.txt','r') as f:
                for line in f:
                    val  = float(line.split()[0]);
                    key =  tuple(line.split()[1:]);
                    dict[key] = val;
            metrics[filename]=dict;
        topic_ranking = rank_topic(metrics,D[file_idx][file_idx]);
        
        print_freq_itemsets(topic_ranking.items(),'./bonus_ranking/bonus_ranking-%d.txt'%file_idx,None);
    
# def print_bonus_ranking(freq_itemsets,purity,filename):
#     file = open(filename,'w');
#     freq_itemsets = sorted(freq_itemsets,key=lambda (iset,msp): msp ,reverse=True);
#     for (itemset,min_sup) in freq_itemsets:
#         pur = purity[itemset];
#         itemset = list(itemset);
#         #convert from numbers to words and sort
#         print >>file, ("%.3f "+ " %s"*len(itemset))%tuple([pur]+itemset);
#     file.close();
#     print "Wrote file ",filename;
#     return;
                    
def calculate_itemsets(topic_file_dir,msp,method,vocabfile):
    '''processes all topic-x files in topic file dir and generates the corresponding
    pattern,closed,max and purity files'''
    
    if method=='apriori':
        algo = mine_apriori;
    elif method=='fpgrowth':
        algo = min_fpgrowth;
    
    vocabulary = build_vocab_dict(vocabfile);
    topic_filenames = os.listdir(topic_file_dir);
    topic_filenames = [filename for filename in topic_filenames if os.path.isfile(topic_file_dir+'/'+filename) and filename.find('topic-')==0];
    file_idx = [int(fileidx(tf)) for tf in topic_filenames];
    file_idx.sort();
    
    freq_itemsets=[];
    closed_freq_itemsets=[];
    maximal_freq_itemsets=[];
    freq_patt_filenames=[];
    #do all first 2 steps for each file
    for file_id in file_idx:
        data = read_transaction_file(topic_file_dir+'/'+'topic-'+str(file_id)+'.txt');
        total_trans = len(data);
        min_sup = float(msp);
        #calculate the frequencies of just the frequent patterns
        freq_itemsets=algo(data,min_sup,total_trans);
        closed_freq_itemsets,maximal_freq_itemsets=find_closed_maximal_freq_itemsets(freq_itemsets,min_sup,total_trans);
        
        #convert the support counts to support values (0-1)
        freq_itemsets = [(pattern,float(supp_count)/total_trans) for (pattern,supp_count) in freq_itemsets];
        closed_freq_itemsets = [(pattern,float(supp_count)/total_trans) for (pattern,supp_count) in closed_freq_itemsets];
        maximal_freq_itemsets = [(pattern,float(supp_count)/total_trans) for (pattern,supp_count) in maximal_freq_itemsets];
        
        print_files = [('./patterns','pattern',freq_itemsets),
                       ('./closed','closed',closed_freq_itemsets),
                       ('./max','max',maximal_freq_itemsets)];
        for dir,fname,print_list in print_files:
            try:    os.mkdir(dir);
            except OSError as e:
                if e.errno==errno.EEXIST : pass;
            fname = dir+'/'+fname+'-'+str(file_id)+'.txt';
            print_freq_itemsets(print_list,fname,vocabulary);
        freq_patt_filenames+=['./patterns/pattern-'+str(file_id)+'.txt'];
    
    #calculate the purity for each topic after the patterns for each topic have been generated
    
    D = [[10047,17326,17988,17999,17820],
         [17326,9674,17446,17902,17486],
         [17988,17446,9959,18077,17492],
         [17999,17902,18077,10161,17912],
         [17820,17486,17492,17912,9845]
        ];
    
    # calculate the purity of each of the itemsets , then use that to print purity and ranking in purity
    # files based on a combined measure of purity and support 
    calculate_purity_support_ranking(freq_patt_filenames,msp,D,vocabulary);
    
    # now calculate the new rank of each of the patterns based on data in frequent, closed, max and purity sets
    calculate_new_ranking(topic_file_dir,D);
        
def build_vocab_dict(vocabfile):
    vocabulary=[];
    with open(vocabfile,'r') as file:
        for line in file:
            word = line.split()[1];
            vocabulary += [word];
    return vocabulary;

if __name__=='__main__':

    #sys.argv += ['./topics','vocab.txt','0.001','fpgrowth'];
    if len(sys.argv)!=5:
        print "Usage: %s topic_file_dir vocabfile min_sup method[apriori,fpgrowth]"%sys.argv[0];
    else:
        calculate_itemsets(sys.argv[1],sys.argv[3],sys.argv[4],sys.argv[2]);
    
    
