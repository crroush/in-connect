from collections import Counter
import numpy as np
import argparse
import re

def bigram( aa ):
   ''' 
   Computes the bigram of an input string 
   The assumption is the string is concatenated 
   "".join(aa)  otherwise it will use spaces
   '''
   res = Counter( aa[idx : idx + 2] \
                  for idx in range( len(aa) -1 ))
   return res

def cosine_sim( aa_c, bb_c ):
   '''
   Computes the Cosine Similarity between two Counters
   aa . bb / (|aa||bb|) = cos(Θ)
      
   '''
   intersec = set(aa_c).intersection(set(bb_c))
   num = sum( [aa_c[xx]*bb_c[xx]  **2 for xx in intersec ]) 
   sum_aa = sum( [aa_c[xx] **2 for xx in aa_c.keys() ]) 
   sum_bb = sum( [bb_c[xx] **2 for xx in bb_c.keys() ]) 
   den = np.sqrt( sum_aa) * np.sqrt( sum_bb )
   
   return  num/den 

def cosine_ngram( aa, bb ):
   '''
   Computes the Cosine Similarity between two Counters
   that are grouped in digraphs "STRING" = "ST RI NG" as
   the tokens
   aa . bb / (|aa||bb|) = cos(Θ)

   '''
   aa_c = bigram( "".join(aa.keys()) )
   bb_c = bigram( "".join(bb.keys()) )
   return cosine_sim( aa_c, bb_c ) 
    
def main():
   # get rid of punctuation
   txt_filt = re.compile( r"\w+" )

   # Some simple company names
   companies = []
   companies.append( "BLUE Farm Inc" )
   companies.append( "blue farm" )
   companies.append( "blue farm, Inc" )
   companies.append( "Blue Farm Inc." )
   filt_names = [] 
   for company in companies:
      # Remove all the punctuation, and lower case everything
      words = txt_filt.findall(company)
      words = [ word.lower() for word in words ]
      filt_names.append(Counter(words))

   sim = cosine_sim( filt_names[1],  filt_names[2] ) 
   nsim = cosine_ngram( filt_names[1], filt_names[2] ) 

   print( "Sim = %f"%(sim))
   print( "Ngram Sim = %f"%(nsim))


if __name__ == "__main__":
   main()
