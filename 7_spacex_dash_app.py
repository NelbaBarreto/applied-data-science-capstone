# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_site_options = spacex_df['Launch Site'].unique()
launch_site_options = np.append(launch_site_options, 'All Sites')

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(launch_site_options, 
                                value='All Sites', 
                                id='site-dropdown',
                                placeholder="Select a Launch Site",
                                searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(min=min_payload, 
                                max=max_payload,
                                id='payload-slider',
                                step=1000,
                                # marks={0: '0', 1000: '1000'},
                                value=[min_payload, max_payload]),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                 ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output("success-pie-chart", "figure"), 
    Input("site-dropdown", "value"))
def generate_pie_chart(site):
    if site == "All Sites":
        fig = px.pie(spacex_df, values='class', names='Launch Site')
    else:
        def get_class_description(class_description):
            if class_description:
                return "Success"
            else:
                return "Failed"
        
        df = spacex_df[spacex_df["Launch Site"] == site]
        df["class_description"] = df["class"].apply(get_class_description)
        df = df.groupby("class_description")["class"].count().reset_index()

        fig = px.pie(df, values="class", names="class_description")

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'), 
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def generate_scatter_chart(site, payload):
    if site == "All Sites":
        df = spacex_df
    else:
        df = spacex_df[spacex_df["Launch Site"] == site]

    df = df[(df["Payload Mass (kg)"] >= payload[0]) & (df["Payload Mass (kg)"] <= payload[1])]
    fig = px.scatter(df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category"
    )
    
    fig.update_yaxes(type='category')

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()