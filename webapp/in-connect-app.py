import numpy as np
import json
from textwrap import dedent as dd
import dash
import dash_bootstrap_components as dbc
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import argparse

import plotly.graph_objects as go
import plotly.express as px

import collections
import bigram
parser = argparse.ArgumentParser()
parser.add_argument("csv_fname",
                     help="Exported CSV file Connections.csv from LinkedIn",
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
df["Name"] = df["First Name"] + " " + df["Last Name"]
#df["Connected On"] = pd.to_datetime(df["Connected On"], format="%d %b %Y")
#df.sort_values( "Connected On", inplace=True )
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
                           "Name"     : df.iloc[ii]["Name"],
                           "Position" : df.iloc[ii]["Position"],
                           "Connected On" : df.iloc[ii]["Connected On"],
                           "idx"      : ii})

max_ppl = max([len(clusters[xx]) for xx in clusters])

# Web stuff
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.layout = html.Div( [
                dcc.Graph(id="scatter-plot"),
                    #html.P("LinkedIn Connections by Company"),
                dcc.RangeSlider(
                        id='range-slider',
                        min=0, max=max_ppl, step=1,
                        marks={0:'0', max_ppl:'%s'%(max_ppl)},
                        value=[0,max_ppl],
                        tooltip={'placement': 'top', 'always_visible': True},
                ),
                dash_table.DataTable(
                    id='table',
                    columns=(
                        [{'id': p, 'name': p} for p in clusters[0][0].keys()]
                    ),
                    editable=True,
                    style_table={'overflowX':'scroll'},
                    style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                    style_cell={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white',
                        'text-align': 'center',
                        }
                    )
                ])
@app.callback(
     Output( "table", "data"),
    [Input( 'scatter-plot', 'hoverData')])
def display_hover_data(hoverData):
    if hoverData == None: return
    cluster = clusters[hoverData['points'][0]['x']]
    return cluster
    try:
        print( hoverData['points'][0]['x'])
        print( clusters[hoverData['points'][0]['x']])
        val = json.dumps( clusters[hoverData['points'][0]['x']], indent=2 )
        print( val )
        return val
    except:
        return None

@app.callback(
    Output( "scatter-plot", "figure"),
    [Input( "range-slider", "value")])
def update_company_chart( slider_range ):
    low, high = slider_range
    hover_text  = []
    bubble_size = []
    # Print the clusters to stdout
    fig = go.Figure()
    for key, val in clusters.items():
       names = []
       companies = []
       if ( len(val) < low or len(val) > high ): continue
       for name in val:
          names.append( name["Name"] )
          if ( key != -1 ):
             companies.append( name["Company"])
          else:
             companies.append( "Not Clustered" )
       bsize = ( len(names) )
       fig.add_trace( go.Scatter( x=[key], y=[bsize],name=companies[0], text=companies[0], marker_size=bsize ))

    fig.update_traces(mode='markers', marker=dict(sizemode='area', line_width=2 ))
    fig.update_layout( title="LinkedIn Network",
                       yaxis=dict( title="Number of Contacts" ),
                       xaxis=dict( title="Companies" ),
                       legend={'traceorder':'grouped'},
                       template="plotly_dark")
    return fig

app.run_server(debug=True)
