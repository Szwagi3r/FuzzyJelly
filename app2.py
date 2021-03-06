import base64
import datetime
import io

import dash
import dash.dash_table as dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State

from fuzzy_set import FuzzySet

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("Distance based diagnostics",
            style={'textAlign': 'center'}
            ),

    html.Div(id='input-box-1',
             children=[
                 dcc.Upload(
                     id='upload-data',
                     children=html.Div([
                         'Choose Patients Dataset or ',
                         html.A('Select Files')
                     ]),
                     # Allow multiple files to be uploaded
                     multiple=True
                 ),

                 html.Div(id='output-data-upload')
             ], style={
            'width': '45%',
            'height': '60px',
            'left': '7%',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'marginLeft': '4%',
            'float': 'left'
        },
             ),
    html.Div(id='input-box-2',
             children=[
                 dcc.Upload(
                     id='upload-data2',
                     children=html.Div([
                         'Choose Diseases Dataset or ',
                         html.A('Select Files')
                     ]),
                     # Allow multiple files to be uploaded
                     multiple=True
                 ),
                 html.Div(id='output-data-upload2')
             ],
             style={
                 'width': '45%',
                 'height': '60px',
                 'lineHeight': '60px',
                 'borderWidth': '1px',
                 'borderStyle': 'dashed',
                 'borderRadius': '5px',
                 'textAlign': 'center',
                 'marginRight':'4%',
                 'float':'right'
             }),
    dcc.Store(id="results1"),
    dcc.Store(id="results2"),
    dcc.Store(id="e"),
    dcc.Store(id="m"),
    dcc.Store(id="a"),
    dcc.Store(id="s"),

    html.Div(dcc.RadioItems(id='input-radio-button',
                            options=[{'label': 'Euclidean', 'value': 'Euclidean'},
                                     {'label': 'Min-Max-Min', 'value': 'Min-Max-Min'},
                                     {'label': 'Absolute', 'value': 'Absolute'},

                                     ],
                            value='Euclidean',
                            labelStyle={'display': 'inline-block'}
                            ),
             style={
                 "bottom": "45%",
                 "left": "45%",
                 "position": "absolute",
                 'textAlign': 'center',
                 'margin-left': 'auto',
                 'margin-right': 'auto',
                 'float': 'center'
             }, ),
    html.Div(id="metric",
             style={
                 "bottom": "30%",
                 "position": "absolute",
                 'width': '50%',
                 'left': '25%',
                 'height': '60px',
                 'lineHeight': '60px',
                 'textAlign': 'center',
                 'display': 'block',
                 'margin-left': 'auto',
                 'margin-right': 'auto',
                 'float': 'center'
             })
],

)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    df = FuzzySet(df=df).df_compressed.astype(str)
    df = df.reset_index()
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],

        ),

        html.Hr(),  # horizontal line

    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-data-upload2', 'children'),
              Input('upload-data2', 'contents'),
              State('upload-data2', 'filename'),
              State('upload-data2', 'last_modified'))
def update_output2(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('results1', 'data'),
              Input('upload-data', 'contents'))
def store_data1(contents1):
    content_type1, content_string1 = contents1[0].split(',')
    decoded1 = base64.b64decode(content_string1)
    df1 = pd.read_csv(io.StringIO(decoded1.decode('utf-8')))
    return df1.to_json(date_format='iso', orient='split')


@app.callback(Output('results2', 'data'),
              Input('upload-data2', 'contents'))
def store_data1(contents2):
    content_type2, content_string2 = contents2[0].split(',')
    decoded1 = base64.b64decode(content_string2)
    df1 = pd.read_csv(io.StringIO(decoded1.decode('utf-8')))
    return df1.to_json(date_format='iso', orient='split')


@app.callback(Output('e', 'data'),
              Input('results1', 'data'),
              Input('results2', 'data'), )
def calculate_metrics(contents1, contents2):

    df1 = pd.read_json(contents1, orient='split')
    df2 = pd.read_json(contents2, orient='split')

    fuzzy_set1 = FuzzySet(df=df1)
    fuzzy_set2 = FuzzySet(df=df2)

    d = fuzzy_set2.distance_diagnosis(fuzzy_set1, dist_type="euclidean")

    return d.diagnosis.to_json(date_format='iso', orient='split')


@app.callback(Output('m', 'data'),
              Input('results1', 'data'),
              Input('results2', 'data'), )
def calculate_metrics(contents1, contents2):

    df1 = pd.read_json(contents1, orient='split')
    df2 = pd.read_json(contents2, orient='split')

    fuzzy_set1 = FuzzySet(df=df1)
    fuzzy_set2 = FuzzySet(df=df2)

    d = fuzzy_set2.min_max_min(fuzzy_set1)

    return d.diagnosis.to_json(date_format='iso', orient='split')

@app.callback(Output('a', 'data'),
              Input('results1', 'data'),
              Input('results2', 'data'), )
def calculate_metrics(contents1, contents2):

    df1 = pd.read_json(contents1, orient='split')
    df2 = pd.read_json(contents2, orient='split')

    fuzzy_set1 = FuzzySet(df=df1)
    fuzzy_set2 = FuzzySet(df=df2)

    d = fuzzy_set2.distance_diagnosis(fuzzy_set1, dist_type="absolute")

    return d.diagnosis.to_json(date_format='iso', orient='split')

@app.callback(Output("metric", "children"),
              Input('m', 'data'),
              Input('e', 'data'),
              Input('a', 'data'),
              Input('input-radio-button', 'value'))
def generate_result_table(m, e, a, radio):
    df1 = pd.read_json(e, orient='split')
    df2 = pd.read_json(m, orient='split').reset_index().round(2)
    df3 = pd.read_json(a, orient='split')

    if radio == "Euclidean":

        return dash_table.DataTable(
            data=df1.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df1.columns],


        )
    elif radio == "Min-Max-Min":
        return dash_table.DataTable(
            data=df2.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df2.columns],

        )
    elif radio == "Absolute":
        return dash_table.DataTable(
            data=df3.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df3.columns],

        )

    else:
        return html.Div("NO METRIC FOUND")


if __name__ == '__main__':
    app.run_server(debug=True)
