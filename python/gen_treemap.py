import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import argparse

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
   df["Company"] = df["Company"].str.lower() 
   df["name"] = df["First Name"] + " " + df["Last Name"]

    
   fig = px.treemap(df, path=[ 'Company', 'Position', 'name' ], 
                    width=1200, height=1200, color='Company')
   fig.show()

if __name__ == "__main__":
   main()
