import dash_core_components as dcc
from django_plotly_dash import DjangoDash
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

now = datetime.datetime.now()
app_name = "DashPlot"
styles = {
    'graph': {
        'width': '99%',
        'height': '100%',
        'display':'inline-block',
    }
}

dashboard_name = 'PutNameFromHtmlPageHere'
box_chart = DjangoDash(name=dashboard_name)

box_chart.layout = html.Div([
    html.P("Show point data"),
    dcc.RadioItems(
        id='show-points',
        options=[{'value': x, 'label': x}
                 for x in ['outliers', 'all']],
        value='outliers',
        labelStyle={'display': 'inline-block', 'margin': '1px 10px 1px 10px'},
    ),
    dcc.Graph(id='boxplot-div',  style=styles['graph'])
])

@box_chart.callback(
    Output(component_id='boxplot-div', component_property='figure'),
    [Input(component_id='show-points', component_property='value')])
def callback_initial(point_type, *args, **kwargs):
    sql = f"""select col1, col2 from tableX
        """
    col1 = []
    col2 = []
    for i, p in enumerate(LayerData.objects.raw(sql)):
        col1.append(p.col1)
        col2.append(p.col2)

    d = {'var1':col1, 'var2':col2}
    df = pd.DataFrame(data=d, columns=['var1', 'var2'])
    df = df.apply(pd.to_numeric)
    fig = px.box(df, x='var1', y='var2', color='var1',  points=point_type)
    fig.update_traces(quartilemethod='inclusive', boxmean=True,)

    return fig
