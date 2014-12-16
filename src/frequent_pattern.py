#!/usr/bin/env python
import fp_mine
import sys
if __name__=="__main__":
    data = fp_mine.read_transaction_file(sys.argv[1]);
    min_sup = float(sys.argv[2])
    total_trans = len(data);
    freq_itemsets = fp_mine.min_fpgrowth(data,min_sup,total_trans); 
    if sys.argv[3]=='freq':
        freq_itemsets = sorted(freq_itemsets,key=lambda x: x[1] , reverse = True);
        for itemset ,  msp in freq_itemsets:
            print itemset," ",msp 
    if sys.argv[3]=='closed':
        closed_itemsets, maximal_itemsets = fp_mine.find_closed_maximal_freq_itemsets(freq_itemsets,min_sup,total_trans)
        closed_itemsets = sorted(closed_itemsets,key=lambda x: x[1] , reverse = True);
        for itemset ,  msp in closed_itemsets:
            print itemset," ",msp 
    if sys.argv[3]=='max':
        closed_itemsets, maximal_itemsets = fp_mine.find_closed_maximal_freq_itemsets(freq_itemsets,min_sup,total_trans)
        maximal_itemsets = sorted(maximal_itemsets,key=lambda x: x[1] , reverse = True);
        for itemset ,  msp in maximal_itemsets:
            print itemset," ",msp 

        
    
    
 
