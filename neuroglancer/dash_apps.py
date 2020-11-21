'''Dash demonstration application

TODO attribution here
'''

# The linter doesn't like the members of the html and dcc imports (as they are dynamic?)
#pylint: disable=no-member
import json

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
from neuroglancer.models import UrlModel
from brain.models import ScanRun
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd


app_name = "ScatterBrain"
styles = {
    'slider': {
        'border': 'thin lightgrey solid',
        'height':'70'
    }
}

dashboard_name = 'ScatterPoint'
scatter_points = DjangoDash(name=dashboard_name,
                           serve_locally=True,
                           app_name=app_name,
                           add_bootstrap_links=True
                          )

scatter_points.layout = html.Div(id='main', children=[
    html.Div([html.H6(id='selected-data')]),
    html.Div(id='section-slider'),
    html.Div(id='output-div'),

]) # end of 'main'

@scatter_points.expanded_callback(
    Output('output-div', 'children'),
    [Input('section-slider', 'value')])

def callback_initial(section, *args, **kwargs): #pylint: disable=unused-argument
    'Callback to generate test data on each change of the dropdown'
    pk = kwargs['session_state']['pk']
    pk = int(pk)
    urlModel = UrlModel.objects.get(pk=pk)
    animal = urlModel.animal
    scanRun = ScanRun.objects.get(prep_id__exact=animal)
    df = urlModel.points
    df = df[(df.Layer == 'PM nucleus') | (df.Layer == 'premotor')]
    sections = df['Section'].sort_values().unique().tolist()
    #section = 272
    if section is None:
        section = df['Section'].min()
    img_width = scanRun.width
    img_height = scanRun.height
    section_min = df['Section'].min()
    section_max = df['Section'].max()
    print('section is ', section, img_width, img_height)
    df = df.loc[ df['Section'] == section]
    section = str(section).zfill(3)
    source = f"https://activebrainatlas.ucsd.edu/data/{animal}/www/{section}.png"

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
    title = f"{urlModel.comments}, section {section}"
    fig.update_layout(title=title)
    fig.update_xaxes(range=[0, img_width])
    fig.update_yaxes(range=[0, img_height], scaleanchor="x")
    fig.update_layout(template="plotly_white")
    fig['layout']['yaxis']['autorange'] = "reversed"
    fig['layout']['height'] = 600
    scatter = fig.data[0]

    scatter.marker.opacity = 1
    scatter.marker.size = 6
    scatter.marker.color = 'yellow'

    scatter_plot = dcc.Graph(id='main-scatter', figure=fig,
                           style={'display': 'inline-block', 'width': '100%',
                           'height': '100%;'})

    slider = html.Div([
        dcc.Slider(
            id='section-slider',
            min=section_min,
            max=section_max,
            value=section,
            marks={k:{'label':str(k),
                      'style':{'color':'blue',
                               'padding-bottom':5,
                               'fontSize':9,
                               'writing-mode':'vertical-rl',
                               'text-orientation':'upright'}} for k in sections},
            step=None
        )
    ], style=styles['slider'])

    tablecols = ['Layer', 'X', 'Y', 'Section']
    t = go.FigureWidget([go.Table(
        header=dict(values=tablecols,
                    fill=dict(color='#C2D4FF'),
                    align=['left'] * 5),
        cells=dict(values=[df[col] for col in tablecols],
                   fill=dict(color='#F5F8FF'),
                   align=['left'] * 5))])

    datatable = dcc.Graph(id='main-table', figure=t)

    children = [scatter_plot, slider, datatable]
    return children

@scatter_points.callback(
    Output('selected-data', 'children'),
    [Input('main-scatter', 'selectedData')])
def display_selected_data(selectedData, *args, **kwargs):
    results = "Use the lasso or box to select points"
    if selectedData is not None and 'points' in selectedData:
        points = selectedData['points']
        results = f"You have selected {len(points)} point"
        if len(points) > 1:
            results += "s"
    return results

##### Next App

dashboard_name = 'ScatterTest'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash(name="ScatterTest",
                 app_name=app_name,
                 external_stylesheets=external_stylesheets
                 )


df = pd.DataFrame({
    "x": [1,2,1,2],
    "y": [1,2,3,4],
    "customdata": [1,2,3,4],
    "fruit": ["apple", "apple", "orange", "orange"]
})

fig = px.scatter(df, x="x", y="y", color="fruit", custom_data=["customdata"])

fig.update_layout(clickmode='event+select')

fig.update_traces(marker_size=20)

app.layout = html.Div([
    dcc.Graph(
        id='basic-interactions',
        figure=fig
    ),

    html.Div(className='row', children=[
        html.Div([
            dcc.Markdown("""
                **Hover Data**
                Mouse over values in the graph.
            """),
            html.Pre(id='hover-data', style=styles['slider'])
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Click Data**
                Click on points in the graph.
            """),
            html.Pre(id='click-data', style=styles['slider']),
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Selection Data**
                Choose the lasso or rectangle tool in the graph's menu
                bar and then select points in the graph.
                Note that if `layout.clickmode = 'event+select'`, selection data also
                accumulates (or un-accumulates) selected data if you hold down the shift
                button while clicking.
            """),
            html.Pre(id='selected-data', style=styles['slider']),
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Zoom and Relayout Data**
                Click and drag on the graph to zoom or click on the zoom
                buttons in the graph's menu bar.
                Clicking on legend items will also fire
                this event.
            """),
            html.Pre(id='relayout-data', style=styles['slider']),
        ], className='three columns')
    ])
])


@app.callback(
    Output('hover-data', 'children'),
    [Input('basic-interactions', 'hoverData')])
def display_hover_data(hoverData, *args, **kwargs):
    return json.dumps(hoverData, indent=2)


@app.callback(
    Output('click-data', 'children'),
    [Input('basic-interactions', 'clickData')])
def display_click_data(clickData, *args, **kwargs):
    return json.dumps(clickData, indent=2)


@app.callback(
    Output('selected-data', 'children'),
    [Input('basic-interactions', 'selectedData')])
def display_selected_data(selectedData, *args, **kwargs):
    return json.dumps(selectedData, indent=2)


@app.callback(
    Output('relayout-data', 'children'),
    [Input('basic-interactions', 'relayoutData')])
def display_relayout_data(relayoutData, *args, **kwargs):
    return json.dumps(relayoutData, indent=2)


##### redone app

dashboard_name = 'ScatterSlider'
scatter_slider = DjangoDash(name=dashboard_name,
                           serve_locally=True,
                           app_name=app_name,
                           add_bootstrap_links=True
                          )

sections = [200,205,240,250,300,310]
scatter_slider.layout = html.Div([
    dcc.Graph(id='main-scatter'),
    dcc.Slider(id='section-slider')
])



@scatter_slider.expanded_callback(
    Output('main-scatter', 'figure'),
    [Input('section_slider', 'value')])

def callback_initial(section, *args, **kwargs): #pylint: disable=unused-argument
    'Callback to generate test data on each change of the dropdown'
    pk = kwargs['session_state']['pk']
    pk = int(pk)
    urlModel = UrlModel.objects.get(pk=pk)
    animal = urlModel.animal
    scanRun = ScanRun.objects.get(prep_id__exact=animal)
    df = urlModel.points
    df = df[(df.Layer == 'PM nucleus') | (df.Layer == 'premotor')]
    sections = df['Section'].sort_values().unique().tolist()
    #section = 272
    if section is None:
        section = df['Section'].min()
    img_width = scanRun.width
    img_height = scanRun.height
    print('section is ', section, img_width, img_height)
    df = df.loc[ df['Section'] == section]
    section = str(section).zfill(3)
    source = f"https://activebrainatlas.ucsd.edu/data/{animal}/www/{section}.png"

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
    title = f"{urlModel.comments}, section {section}"
    fig.update_layout(title=title)
    fig.update_xaxes(range=[0, img_width])
    fig.update_yaxes(range=[0, img_height], scaleanchor="x")
    fig.update_layout(template="plotly_white")
    fig['layout']['yaxis']['autorange'] = "reversed"
    fig['layout']['height'] = 600
    scatter = fig.data[0]

    scatter.marker.opacity = 1
    scatter.marker.size = 6
    scatter.marker.color = 'yellow'

    scatter_plot = dcc.Graph(id='main-scatter', figure=fig,
                           style={'display': 'inline-block', 'width': '100%',
                           'height': '100%;'})
    dropdown = html.Div([
                 dcc.Dropdown(
                     id='section_dropdown',
                     options=[{'label':k, 'value': k} for k in sections],
                     value=section,
                     className='col-md-12',
                 )])


    tablecols = ['Layer', 'X', 'Y', 'Section']
    t = go.FigureWidget([go.Table(
        header=dict(values=tablecols,
                    fill=dict(color='#C2D4FF'),
                    align=['left'] * 5),
        cells=dict(values=[df[col] for col in tablecols],
                   fill=dict(color='#F5F8FF'),
                   align=['left'] * 5))])

    datatable = dcc.Graph(id='main-table', figure=t)

    children = [scatter_plot, dropdown, datatable]
    return fig

@scatter_slider.callback(
    Output('selected-data', 'children'),
    [Input('main-scatter', 'selectedData')])
def display_selected_data(selectedData, *args, **kwargs):
    results = "Use the lasso or box to select points"
    if selectedData is not None and 'points' in selectedData:
        points = selectedData['points']
        results = f"You have selected {len(points)} point"
        if len(points) > 1:
            results += "s"
    return results
