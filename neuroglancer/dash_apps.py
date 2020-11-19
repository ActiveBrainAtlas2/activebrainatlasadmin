'''Dash demonstration application

TODO attribution here
'''

# The linter doesn't like the members of the html and dcc imports (as they are dynamic?)
#pylint: disable=no-member

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
#import dpd_components as dpd
import numpy as np
import pandas as pd
from django_plotly_dash import DjangoDash
from neuroglancer.models import UrlModel
from dash.dependencies import Input, Output, State
app_name = "ScatterBrain"

dashboard_name = 'ScatterExample'
scatter_points = DjangoDash(name=dashboard_name,
                           serve_locally=True,
                           app_name=app_name,
                           add_bootstrap_links=True
                          )

scatter_points.layout = html.Div(id='main',
                                children=[
                                    dcc.Dropdown(
                                        id='section_dropdown',
                                        options = [{'label':k, 'value': k} for k in range(100,300)],
                                        value=200,
                                        className='col-md-10',
                                    ),

                                    html.Div(id='output-div')

                                    ]) # end of 'main'

@scatter_points.expanded_callback(
    Output('output-div', 'children'),
    [Input('section_dropdown', 'value')])

def callback_initial(section, *args, **kwargs): #pylint: disable=unused-argument
    'Callback to generate test data on each change of the dropdown'
    pk = kwargs['session_state']['pk']
    pk = int(pk)
    urlModel = UrlModel.objects.get(pk=pk)
    df = urlModel.points
    df = df[(df.Layer == 'PM nucleus') | (df.Layer == 'premotor')]
    sections = df['Section'].unique
    #section = 272
    if section is None:
        section = df['Section'].min()
    img_width = 65000
    img_height = 36000
    print('section is ', section)
    df = df.loc[ df['Section'] == section]
    section = str(section).zfill(3)

    source = f"https://activebrainatlas.ucsd.edu/data/DK52/www/{section}.png"
    fig = go.FigureWidget([go.Scatter(y=df['Y'], x=df['X'], mode='markers')])
    fig.add_layout_image(
        dict(
            x=0,
            sizex=img_width,
            y=0,
            sizey=img_height,
            xref="x",
            yref="y",
            yanchor="top",
            opacity=0.5,
            layer="below",
            name="showme",
            source=source,
            sizing="contain")
    )

    fig.update_layout(title=urlModel.comments)
    fig.update_xaxes(range=[0, img_width])
    fig.update_yaxes(range=[0, img_height], scaleanchor="x")
    fig.update_layout(template="plotly_white")
    fig['layout']['yaxis']['autorange'] = "reversed"

    scatter_plot = dcc.Graph(id='main-scatter', figure=fig,
                           style={'display': 'inline-block', 'width': '100%',
                           'height': '100%;'})
    children = [scatter_plot]
    return children
