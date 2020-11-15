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
import plotly.express as px



# Multi-dropdown options
from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create controls
county_options = [
    {"label": str(COUNTIES[county]), "value": str(county)} for county in COUNTIES
]

well_status_options = [
    {"label": str(WELL_STATUSES[well_status]), "value": str(well_status)}
    for well_status in WELL_STATUSES
]

well_type_options = [
    {"label": str(WELL_TYPES[well_type]), "value": str(well_type)}
    for well_type in WELL_TYPES
]


# Load data
df = pd.read_csv(DATA_PATH.joinpath("wellspublic.csv"), low_memory=False)
df["Date_Well_Completed"] = pd.to_datetime(df["Date_Well_Completed"])
df = df[df["Date_Well_Completed"] > dt.datetime(1960, 1, 1)]

trim = df[["API_WellNo", "Well_Type", "Well_Name"]]
trim.index = trim["API_WellNo"]
dataset = trim.to_dict(orient="index")

# points = pickle.load(open(DATA_PATH.joinpath("points.pkl"), "rb"))


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

#new df
import plotly.graph_objects as go
df1 = pd.read_excel(DATA_PATH.joinpath("data42.xlsx"))
df1['Date'] = pd.to_datetime(df1.Date)
features = df1.columns[1:-1]
opts = [{'label' : i, 'value' : i} for i in features]

# Step 3. Create a plotly figure
trace_1 = go.Scatter(x = df1.Date, y = df1['Gauteng'],
                    name = 'Gauteng',
                    line = dict(width = 2,
                                color = 'rgb(229, 151, 50)'))

layout = go.Layout(title = 'Drought Time Series Plot',
                   hovermode = 'closest')
fig = go.Figure(data = [trace_1], layout = layout)

red_button_style = {'background-color': '#3aaab2',
                    'color': 'black',
                    'height': '30px',
                    'width': '200px',
                    'fontSize' : '15px',
                    #'margin-top': '400px',
                    'margin-left': '100px',
                   }

# create precipitation graph

drought_df = pd.read_csv('data/provincial_drought_data.csv', usecols=['year', 'tot_preci_GP', 'spei_Gauteng', 'spei_status_GP'])

trace_2 = go.Scatter(x = drought_df.year, y = drought_df['tot_preci_GP'],
                    name = 'tot_preci_GP',
                    line = dict(width = 2,
                                color = 'rgb(229, 151, 50)'))

layout = go.Layout(title = 'Avg. Monthly Precipitation (mm)',
                   hovermode = 'closest')
fig2 = go.Figure(data = [trace_2], layout = layout)

red_button_style = {'background-color': '#3aaab2',
                    'color': 'black',
                    'height': '30px',
                    'width': '200px',
                    'fontSize' : '15px',
                    #'margin-top': '400px',
                    'margin-left': '100px',
                   }

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
                            href="https://web-chat.global.assistant.watson.cloud.ibm.com/preview.html?region=eu-gb&integrationID=46d49594-3509-4483-8901-8df23121a8c8&serviceInstanceID=567bedbe-3dcb-4f17-b50b-fadcc811234a",
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
                        
                        dcc.Dropdown(
                            id="well_statuses",
                            options=well_status_options,
                            multi=False,
                            value=list(WELL_STATUSES.keys()),
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
                                {"label": "Gauteng ", "value": "productive"},
                                {"label": "North West ", "value": "custom"},
                            ],
                            value="productive",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="well_types",
                            options=well_type_options,
                            multi=True,
                            value=list(WELL_TYPES.keys()),
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
                        html.Div(
                            [dcc.Graph(id="count_graph", figure=fig)],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),

        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="bar_graph", figure=fig2)], # changed pie to bar
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="aggregate_graph")], # aggregate to bar
                    className="pretty_container five columns",
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
