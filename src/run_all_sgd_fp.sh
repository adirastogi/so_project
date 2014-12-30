./multi_class_classifier_fp_sgd.py ../datasets/5000_train.csv 0.8 tags_fpgrowthoutput.txt | tee 5klogsgd_fp.txt 
./multi_class_classifier_fp_sgd.py ../datasets/10000_train.csv 0.8 tags_fpgrowthoutput.txt | tee 10klogsgd_fp.txt
./multi_class_classifier_fp_sgd.py ../datasets/20000_train.csv 0.8 tags_fpgrowthoutput.txt | tee 20klogsgd_fp.txt
./multi_class_classifier_fp_sgd.py ../datasets/40000_train.csv 0.8 tags_fpgrowthoutput.txt | tee 40klogsgd_fp.txt
