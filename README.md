so_project
==========
Dataset taken from https://www.kaggle.com/c/facebook-recruiting-iii-keyword-extraction
Machine Learning project for CS 446

1. Total data size : 6034195 questions
	Data we are taking: 249266 questions training
			    124139 test questions
        Tags kept : tags with support > 50. this gives us 1812 tags.
                    with this , we got 8666 questions for which all the tags were dropped (around 3.46% of data), got rid of this
2. Removed code tags from the body
3. Removed stop words from the text and body
4. Converted to TF-IDF vectors
5. Implemented classifiers
6. More detailed project report in the PDF.
