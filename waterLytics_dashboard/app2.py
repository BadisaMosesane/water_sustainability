# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

df = pd.read_csv("data/provincial_drought_data.csv")

drought_data_gp = pd.read_csv("data/provincial_drought_data.csv", usecols=['prov_name', 'year', 'tot_preci_GP', 'spei_Gauteng', 'spei_status_GP'])
# drought_data_gp['id'] = drought_data_gp['iso_alpha3'] # have an ID for country
# drought_data_gp.set_index('id', inplace=True, drop=False)
# print(drought_data_gp.columns)

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Map Locations",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-22.35, lat=-34.53),
        zoom=7,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("waterlytics-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "WaterLytics: A Drought Monitoring & Prediction Platform",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.P(
                                    "Sustainable water use using Machine Learning", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Predictions", id="learn-more-button"),
                            href="https://plot.ly/dash/pricing/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),

                html.Div(
                    [
                        html.A(
                            html.Button("Chat", id="chatbot"),
                            href="https://bot.dialogflow.com/678ea40c-0ed4-4445-8b0e-d6f473bc5e92",
                        )
                    ],
                    className="one-third column",
                    id="button2",
                ),

            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Filter by date (select date range):",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="year_slider",
                            min=1960,
                            max=2017,
                            value=[1990, 2010],
                            className="dcc_control",
                        ),
                        html.P("Filter by Location:", className="control_label"),
                        dcc.RadioItems(
                            id="well_status_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Gauteng ", "value": "active"},
                                {"label": "Western Cape", "value": "custom"},
                            ],
                            value="active",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="well_statuses",
                            # options=well_status_options,
                            multi=True,
                            # value=list(WELL_STATUSES.keys()),
                            className="dcc_control",
                        ),
                        # dcc.Checklist(
                        #     id="lock_selector",
                        #     options=[{"label": "Lock camera", "value": "locked"}],
                        #     className="dcc_control",
                        #     value=[],
                        # ),
                        html.P("Water-Use Restrictions: ", className="control_label"),
                        dcc.RadioItems(
                            id="well_type_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Household restr ", "value": "productive"},
                                {"label": "Agricultural ", "value": "custom"},
                            ],
                            value="productive",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="well_types",
                            # options=well_type_options,
                            multi=True,
                            # value=list(WELL_TYPES.keys()),
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="well_text"), html.P("Current Water Use (Litres)")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="gasText"), html.P("Regional-Cap")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oilText"), html.P("Current Rainfall")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="waterText"), html.P("Drought status (Category: severe)")],
                                    id="water",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),

                        html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
            if i == "year" or i == "prov_name"
            else {"name": i, "id": i, "deletable": True, "selectable": True}
            for i in drought_data_gp.columns
        ],
        data=drought_data_gp.to_dict('records'),  # the contents of the table
        editable=True,              # allow editing of data inside all cells
        filter_action="native",     # allow filtering of data by user ('native') or not ('none')
        sort_action="native",       # enables data to be sorted per-column by user or not ('none')
        sort_mode="single",         # sort across 'multi' or 'single' columns
        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
        row_selectable="multi",     # allow users to select 'multi' or 'single' rows
        row_deletable=True,         # choose if user can delete a row (True) or not (False)
        selected_columns=[],        # ids of columns that user selects
        selected_rows=[],           # indices of rows that user selects
        page_action="native",       # all data is passed to the table up-front or not ('none')
        page_current=0,             # page number that user is on
        page_size=6,                # number of rows visible per page
        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'minWidth': 95, 'maxWidth': 95, 'width': 95
        },
        style_cell_conditional=[    # align text columns to left. By default they are aligned to right
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['prov_name','spei_Gauteng', 'year', 'tot_preci_GP', 'spei_status_GP']
        ],
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    ),

    html.Br(),
    html.Br(),
    html.Div(id='bar-container'),
    html.Div(id='choromap-container')

])

# -------------------------------------------------------------------------------------
# Create bar chart
@app.callback(
    Output(component_id='bar-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_row_ids'),
     Input(component_id='datatable-interactivity', component_property='selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_indices'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_row_ids'),
     Input(component_id='datatable-interactivity', component_property='active_cell'),
     Input(component_id='datatable-interactivity', component_property='selected_cells')]
)
def update_bar(all_rows_data, slctd_row_indices, slct_rows_names, slctd_rows, order_of_rows_indices, order_of_rows_names, actv_cell, slctd_cell):
    print('***************************************************************************')
    print('Data across all pages pre or post filtering: {}'.format(all_rows_data))
    print('---------------------------------------------')
    print("Indices of selected rows if part of table after filtering:{}".format(slctd_row_indices))
    print("Names of selected rows if part of table after filtering: {}".format(slct_rows_names))
    print("Indices of selected rows regardless of filtering results: {}".format(slctd_rows))
    print('---------------------------------------------')
    print("Indices of all rows pre or post filtering: {}".format(order_of_rows_indices))
    print("Names of all rows pre or post filtering: {}".format(order_of_rows_names))
    print("---------------------------------------------")
    print("Complete data of active cell: {}".format(actv_cell))
    print("Complete data of all selected cells: {}".format(slctd_cell))

    dff = pd.DataFrame(all_rows_data)

    # used to highlight selected provinces on bar chart
    colors = ['#FF9900' if i in slctd_row_indices else '#0074D9'
              for i in range(len(dff))]

    if "year" in dff and "tot_preci_GP" in dff:
        return [
            dcc.Graph(id='bar-chart',
                      figure=px.bar(
                          data_frame=dff,
                          x="year",
                          y='tot_preci_GP',
                          labels={"tot_preci_GP": "Total Precipitation (mm)"}
                      ).update_layout(showlegend=False, xaxis={'categoryorder': 'total ascending'})
                      .update_traces(marker_color=colors, hovertemplate="<b>%{y}%</b><extra></extra>")
                      )
        ]


                        # html.Div(
                        #     [dcc.Graph(id="count_graph")],
                        #     id="countGraphContainer",
                        #     className="pretty_container",
                        #     fig = go.Figure(go.Scatter(x = df['year'], y = df['total_precipitation'],
                        #     name='Total Precipitation (in mm)'))
                        #     # import plotly.graph_objects as go
                        #     # fig.update_layout(title='Province Precipitation over years',
                        #     # plot_bgcolor='rgb(230, 230,230)',
                        #     # showlegend=True)
                        #     # fig.show()
                        # ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

# Main
if __name__ == "__main__":
    app.run_server(debug=True)