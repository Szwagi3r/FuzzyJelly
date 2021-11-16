import base64
import datetime
import io

import dash
import dash.dash_table as dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash import html
from dash.dependencies import Input, Output, State

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


df = pd.read_csv('data/set_1.csv')

# fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

# fig.update_layout(
#     plot_bgcolor=colors['background'],
#     paper_bgcolor=colors['background'],
#     font_color=colors['background']
# )


# always 3 components
# app.layout = html.Div(children=[
#     html.H1(children='Fuzzy jelly'),
#     html.Div(children='''
#         Dash: A web application framework for your data.
#     '''),
#
#     html.H4("Fuzzy set"),
#     generate_table(df)
#
#     # dcc.Graph(
#     #     id='example-graph',
#     #     figure=fig)
# ])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("Intuitionistic Fuzzy Set",
            style={
                'textAlign': 'center'}
            ),
    html.Div(id='input-box-1',
             children=[
                 dcc.Upload(
                     id='upload-data',
                     children=html.Div([
                         'Drag and Drop first fuzzy set or ',
                         html.A('Select Files')
                     ]),
                     # Allow multiple files to be uploaded
                     multiple=True
                 ),

                 html.Div(id='output-data-upload')
             ], style={
            'width': '45%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'float': 'left'
        },
             ),
    html.Div([
        dcc.Upload(
            id='upload-data2',
            children=html.Div([
                'Drag and Drop first fuzzy set or ',
                html.A('Select Files')
            ]),
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.Div(id='output-data-upload2')
    ], style={
        'width': '45%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px',
        'float': 'left'
    },
    ),
])


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

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
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


if __name__ == '__main__':
    app.run_server(debug=True)