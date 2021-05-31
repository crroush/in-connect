import numpy as np
import json
from textwrap import dedent as dd
import dash
import dash_bootstrap_components as dbc
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
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
                           "id"      : ii})

max_ppl = max([len(clusters[xx]) for xx in clusters])

btn_style ={
              "backgroundColor": "#404040",
              "color": "white",
              "text-align": "center",
              "margin-bottom": "5px"
            }
tab_style ={
              "backgroundColor": "#121212",
              "color": "white",
              "text-align": "center",
              "margin-bottom": "5px"
            }

columns=([{'id': p, 'name': p} for p in clusters[0][0].keys()])

# Web stuff

tab_connect = dcc.Tab(label="Connections", value="plot_tab", style=tab_style,
                selected_style={"background": "#404040", "color": "white"} )
tab_annotate = dcc.Tab(label="Annotations", value="annotate_tab", style=tab_style,
                selected_style={"background": "#404040", "color": "white"} )

connect_content = html.Div( [
                      html.Button("Edit", id="edit-contact_btn", n_clicks=0,
                                   style=btn_style),
                      html.Button("Add Interaction", id="inter-contact_btn",
                                   n_clicks=0, style=btn_style),
                      dash_table.DataTable(
                          id='table',
                          columns =
                              [{'id': p, 'name': p} for p in clusters[0][0].keys()],
                          editable=False,
                          row_selectable="multi",
                          column_selectable=False,
                          cell_selectable=False,
                          page_size=5,
                          selected_row_ids = [],
                          style_table={'overflowX':'scroll'},
                          style_header={'backgroundColor': '#181818'},
                          style_cell={
                              'backgroundColor': '#121212',
                              'color': 'white',
                              'text-align': 'center',
                              },
                          style_cell_conditional=[ {'if': {'column_id': 'id', },
                                                  'display': 'None',}]
                          )
                  ])
annotate_content = html.Div([html.H3("Garbage")])

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div( [
               dcc.Graph(id="scatter-plot"),
               dcc.RangeSlider(
                       id='range-slider',
                       min=0, max=max_ppl, step=1,
                       marks={0:'0', max_ppl:'%s'%(max_ppl)},
                       value=[0,max_ppl],
                       tooltip={'placement': 'top', 'always_visible': True},
               ),

    dcc.Tabs( id="tabs", value="plot_tab",
              children=[ tab_connect, tab_annotate ]),
    # Assigning the children to the content allows the callbacks to function
    # properly
    html.Div( id="tabs-content", children=connect_content)
    ])


# Web page callbacks
@app.callback(
        Output("tabs-content", "children"),
        Input( "tabs", "value" ))
def render_content(tab):
    if tab == "plot_tab":
        return connect_content
    if tab == "annotate_tab":
        return annotate_content


@app.callback(
     [Output( "table", "data"),
      Output( "table", "selected_row_ids"),
      Output( "table", "selected_rows" ),
      Output('table', 'page_current')
      ],
    [Input( 'scatter-plot', 'hoverData')])
def display_hover_data(hoverData):
    if hoverData == None: return None, [], [], 0
    cluster = clusters[hoverData['points'][0]['x']]
    return cluster, [], [], 0

@app.callback(
    Output( "scatter-plot", "figure"),
    Input( "range-slider", "value")
    )
def update_company_chart( slider_range):
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

@app.callback(
    Output("table", "style_data_conditional"),
    Input("table", "derived_virtual_selected_row_ids"),
)
def style_selected_rows(sel_rows):
    if sel_rows is None:
        return dash.no_update
    val = [
        {"if": {"filter_query": "{{id}} ={}".format(i)}, "backgroundColor": "#404040",}
        for i in sel_rows
    ]
    return val


app.run_server(debug=True)
