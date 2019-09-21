# -*- coding: utf-8 -*-
import os
import sys

sys.path.remove(os.path.abspath(os.path.dirname(__file__)))

import dash_html_components as html
import dash_core_components as dcc

from dash.dependencies import Input, Output

from zvdata.app import app

from github.domain import init_schema

init_schema()

from zvdata.apps import data_app


def serve_layout():
    layout = html.Div([
        dcc.Tabs(
            id="tabs-with-classes",
            value='tab-2',
            parent_className='custom-tabs',
            className='custom-tabs-container',
            children=[
                dcc.Tab(
                    label='data',
                    value='data',
                    className='custom-tab',
                    selected_className='custom-tab--selected'
                )
            ]),
        html.Div(id='tabs-content-classes')
    ])
    return layout


app.layout = serve_layout


@app.callback(Output('tabs-content-classes', 'children'),
              [Input('tabs-with-classes', 'value')])
def render_content(tab):
    if tab == 'data':
        return data_app.layout


if __name__ == '__main__':
    app.run_server(debug=True)
