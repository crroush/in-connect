from collections import Counter
import collections
import numpy as np
import argparse
import re
from sklearn import cluster #DBScan

def bigram( aa ):
   ''' 
   Computes the bigram of an input string 
   The assumption is the string is concatenated 
   "".join(aa)  otherwise it will use spaces
   '''
   res = Counter( aa[idx : idx + 2] \
                  for idx in range( len(aa) -1 ))
   return res

def cosine_sim( aa, bb):
   '''
   Computes the Cosine Similarity between two Counters
   aa . bb / (|aa||bb|) = cos(Θ)
   '''

   aa_c = Counter(aa)
   bb_c = Counter(bb)
   intersec = set(aa_c).intersection(set(bb_c))
   num = sum( [aa_c[xx]*bb_c[xx]  **2 for xx in intersec ]) 
   sum_aa = sum( [aa_c[xx] **2 for xx in aa_c.keys() ]) 
   sum_bb = sum( [bb_c[xx] **2 for xx in bb_c.keys() ]) 
   den = np.sqrt( sum_aa) * np.sqrt( sum_bb )
   
   return  num/den 

def cosine_ngram( xi, yi, **vals ):
   '''
   Computes the Cosine Distance between two indexs and vals 
   that are grouped in digraphs "STRING" = "ST RI NG" as
   the tokens
   aa . bb / (|aa||bb|) = cos(Θ)

   '''
   vals = vals["names"]
   aa = vals[int(xi)]
   bb = vals[int(yi)]
   aa_c = bigram( "".join(aa) )
   bb_c = bigram( "".join(bb) )

   return 1-cosine_sim( list(aa_c), list(bb_c) ) 
def cleanup_text( text ):
   ''' 
   Cleans up the words, first removes punctuation,
   then lower cases everything.  There are a lot of things you can do here,
   however this is the simpliest way to start.  
   Returns tokenized output
   '''

   txt_filt = re.compile( r"\w+" )
   words = txt_filt.findall(text)
   words = [ word.lower() for word in words ]
   return words 

def cluster_names(token_list):
   ''' 
      takes a list of list of tokens for each name
      clusters the result using the cosine distance
   '''
   # Apply DBSCAN to cluster the results
   vals = {}
   vals["names"] = token_list 
   db = cluster.DBSCAN(metric=cosine_ngram, metric_params=vals, min_samples=2)
   xx = np.arange( len(token_list)).reshape(-1,1)
   clust = db.fit(xx )
   dclusters = collections.defaultdict(list) 
   for ii, label in enumerate(clust.labels_):
      dclusters[label].append(ii)
   return dclusters 

def main():
   # Some simple company names
   companies = []
   # cluster 0
   companies.append( "BLUE Farm Inc" )
   companies.append( "blue farm" )
   companies.append( "blue farm, Inc" )
   companies.append( "Blue Farm Inc." )
   # cluster 1
   companies.append( "Green House Inc.")
   companies.append( "Green House" )
   companies.append( "Green House corp" )
   
   # no cluster (e.g. residual )
   companies.append( "Blah Fake Inc" ) 

   # Clean up the words
   filt_names = [] 
   for company in companies:
      words = cleanup_text( company ) 
      filt_names.append(words) 

   dclusters = cluster_names( filt_names )
   print( dclusters)


if __name__ == "__main__":
   main()
