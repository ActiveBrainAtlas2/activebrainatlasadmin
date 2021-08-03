from neuroglancer.models import LAUREN_ID, LayerData
from neuroglancer.AlignmentScore import AlignmentScore
from plotly.subplots import make_subplots
from neuroglancer.atlas import get_centers_dict
from dash.dependencies import Input, Output
import dash
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('SimpleExample', external_stylesheets=external_stylesheets)   # replaces dash.Dash

align_score = AlignmentScore()
fig = align_score.get('box_plot')
app.layout = html.Div(children=[
    dcc.Graph(id='plot'),
    html.Label('Select plot types'),
    dcc.RadioItems(id = 'type',
        options=[
            {'label': 'scatter plot', 'value': 'scatter'},
            {'label': u'box plot', 'value': 'box_plot'},
        ],
        value='scatter'
    ),
])

@app.callback(
    Output('plot', 'figure'),
    Input('type', 'value'))
def update_figure(figure_type):
    fig = align_score.get(figure_type)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)