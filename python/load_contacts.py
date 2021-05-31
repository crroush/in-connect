import argparse
from elasticsearch import Elasticsearch, helpers
from datetime import datetime
from collections import defaultdict

import pandas as pd
import numpy as np
import bigram

def load_df( df, es_index ):
    records = df.to_dict(orient= 'records')
    for data in records:
        yield {
                "_index": es_index,
                "_source": data
              }

def main():
   parser = argparse.ArgumentParser()
   parser.add_argument("csv_fname",
                        help="Exported CSV file Connections.csv from LinkedIn",
                        type=str)
   parser.add_argument("--es_host", type=str,
                        help="URL of the elasticsearch host", default="localhost" )
   parser.add_argument("--es_port", type=str,
                        help="elasticsearch host port", default="9200" )
   parser.add_argument("--es_index", type=str,
                        help="elasticsearch index for the data", default="linkedin" )

   args = parser.parse_args()

   df = pd.read_csv( args.csv_fname,
                     quotechar='"', escapechar="/", skiprows=[0,1,2])

   df = df.replace(np.nan, '', regex=True )
   df = df[df.Company != '']
   df["name"]    = df["First Name"] + " " + df["Last Name"]

   es = Elasticsearch( [{'host': args.es_host, 'port': "%s"%args.es_port}])
   helpers.bulk( es, load_df( df, args.es_index ))

if __name__ == "__main__":
    main()
