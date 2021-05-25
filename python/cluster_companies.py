import numpy as np
import pandas as pd
import plotly
import collections
import argparse

import plotly.graph_objects as go
import plotly.express as px

import bigram
def main():
   parser = argparse.ArgumentParser()
   parser.add_argument("csv_fname", 
                        help="Exported CSV file Connections.csv from LinkedIn", \
                        type=str)
   args = parser.parse_args()
   
   # Note the csv file names can have quotes, so we need to escape them
   # Currently the first 3 rows are not part of the standard export (22May2021)
   # Since I do not control the source export utility, skiprows may need to change
   # to handle this.
   df = pd.read_csv( args.csv_fname, 
                     quotechar='"', escapechar="/", skiprows=[0,1,2])

   df = df.replace(np.nan, '', regex=True )
   df = df[df.Company != '']
   df["name"]    = df["First Name"] + " " + df["Last Name"]

   filt_names = [] 
   for company in df["Company"]:
      words = bigram.cleanup_text( company ) 
      filt_names.append(words) 
   
   db = bigram.cluster_names( filt_names )

   labels = db.labels_
   # Number of clusters in labels, ignoring noise if present.
   n_clusters  = len(set(labels)) - (1 if -1 in labels else 0)
   n_noise     = list(labels).count(-1)
   

   xx = np.arange( len(filt_names)).reshape(-1,1)

   clusters = collections.defaultdict(list) 
   for ii, label in enumerate(labels):
      clusters[label].append({"Company"  : df.iloc[ii]["Company"],
                              "Name"     : df.iloc[ii]["name"],
                              "Position" : df.iloc[ii]["Position"],
                              "idx"      : ii})

   hover_text  = []    
   bubble_size = []
   # Print the clusters to stdout
   fig = go.Figure()
   for key, val in clusters.items():
      names = []
      companies = []
      for name in val:
         print( "%d %s - %s"%(key, name["Company"], name["Name"] ))
         names.append( name["Name"] )
         if ( key != -1 ):
            companies.append( name["Company"])
         else:
            companies.append( "Not Clustered" )
      htext = ("Company: " + companies[0] + "<br>Contacts:<br>" + "<br>".join(names))
      bsize = ( len(names) )
      fig.add_trace( go.Scatter( x=[key], y=[bsize],name=companies[0], text=htext, marker_size=bsize ))


      print( "========================" )
   fig.update_traces(mode='markers', marker=dict(sizemode='area', line_width=2 ))
   fig.update_layout( title="LinkedIn Network", 
                      yaxis=dict( title="Number of Contacts" ),
                      xaxis=dict( title="Companies" ),
                      legend={'traceorder':'grouped'})
   fig.show()
   print('Estimated number of clusters: %d' % n_clusters )
   print('Estimated number of noise points: %d' % n_noise )
if __name__ == "__main__":
   main()
