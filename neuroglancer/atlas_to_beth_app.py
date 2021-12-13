from neuroglancer.com_difference.TransformedAtlasToBeth import TransformedAtlasToBeth
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

atlas_to_beth_app = DjangoDash('AtlasToBeth',external_stylesheets=external_stylesheets)

atlas_to_beth_app.layout = html.Div(children=[
    dcc.Graph(id='plot'),
    html.Label('Select plot type'),
    dcc.RadioItems(id='plottype',
            options=[
                {'label': 'scatter plot', 'value': 'scatter'},
                {'label': u'box plot', 'value': 'box_plot'},
            ],
        value='scatter'
    ),
])


@atlas_to_beth_app.expanded_callback(
    Output('plot', 'figure'),
    [Input('plottype', 'value')])
def update_figure(figure_type):
    align_score = TransformedAtlasToBeth()
    fig = align_score.get(figure_type)
    return fig
