import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import argparse

def main():
   parser = argparse.ArgumentParser()
   parser.add_argument("csv_fname",
                        help="Exported CSV file Connections.csv from LinkedIN",
                        type=str)
   parser.add_argument("--network_name",
                        help="Network name for plotting",
                        type=str, default="LinkedIN Network")
   parser.add_argument("--save_html",
                        help="HTML page to save",
                        type=str, default=None )
   args = parser.parse_args()

   # Note the csv file names can have quotes, so we need to escape them
   # Currently the first 3 rows are not part of the standard export (22May2021)
   # Since I do not control the source export utility, skiprows may need to change
   # to handle this.
   df = pd.read_csv( args.csv_fname,
                     quotechar='"', escapechar="/", skiprows=[0,1,2])

   df = df.replace(np.nan, '', regex=True )
   df = df[df.Company != '']
   df["Network"] = args.network_name
   df["Company"] = df["Company"].str.lower()
   df["name"]    = df["First Name"] + " " + df["Last Name"]


   fig = px.treemap(df, path=[ 'Network', 'Company', 'Position', 'name' ],
                    width=1200, height=1200, color='Company')
   if (args.save_html != None and len(args.save_html) > 0):
       fig.write_html(args.save_html)

   fig.show()

if __name__ == "__main__":
   main()
