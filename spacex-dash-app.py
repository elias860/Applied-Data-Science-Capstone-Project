# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/labs/module_3/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown for Launch Site selection
    html.Div([
        html.Label("Select Launch Site:"),
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
            ],
            value='ALL',
            placeholder="Select a Launch Site",
            searchable=True
        )
    ]),
    html.Br(),
    
    # TASK 2: Add a pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # TASK 3: Add a range slider for payload
    html.Div([
        html.Label("Payload Range (kg):"),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            value=[min_payload, max_payload],
            marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'}
        )
    ]),
    html.Br(),
    
    # TASK 4: Add a scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2 callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For all sites, show total success launches by site
        filtered_df = spacex_df[spacex_df['class'] == 1]
        pie_data = filtered_df.groupby('Launch Site').size().reset_index(name='count')
        fig = px.pie(pie_data, values='count', names='Launch Site', 
                     title='Total Success Launches by Site')
    else:
        # For specific site, show success vs failure counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        pie_data = pd.DataFrame({
            'outcome': ['Success', 'Failure'],
            'count': [success_count, failure_count]
        })
        fig = px.pie(pie_data, values='count', names='outcome',
                     title=f'Success vs Failure for {entered_site}')
    return fig

# TASK 4 callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title='Correlation between Payload and Success for all Sites')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)




# Question 1: Which site has the largest successful launches?

# Answer: KSC LC-39A
# From your pie chart:
# -KSC LC-39A - largest slice (looks like ~40-45%)
# -CCAFS SLC-40 - second largest (~25-30%)
# -CCAFS LC-40 - third (~15-20%)
# -VAFB SLC-4E - smallest (~10-15%)

# Question 2: Which site has the highest launch success rate?

# Answer: KSC LC-39A
# -When you select KSC LC-39A in the dropdown, it shows mostly successes (class=1) with very few failures. This site has the best track record.

# Question 3: Which payload range has the highest launch success rate?

# Answer: 2,000 kg - 4,000 kg (approximately)
# From your scatter plot:
# -Points at y=1 (success) cluster heavily between 2,000-4,000 kg
# -Booster versions FT and B5 in this range are almost all successful

# Question 4: Which payload range has the lowest launch success rate?

# Answer: 0 - 1,000 kg AND 6,000 - 7,000 kg
# From your scatter plot:
# -Light payloads (0-1,000 kg) : Many points at y=0 (failure), especially v1.0
# -Heavy payloads (6,000-7,000 kg) : Mixed results, several failures

# Question 5: Which F9 Booster version has the highest launch success rate?
# Answer: FT

# From your scatter plot colors:

# FT (green/teal points) - Almost all at y=1 (success), very reliable
# B5 - Also very successful
# B4 - Mixed results
# v1.1 - Some successes, many failures
# v1.0 - Mostly failures (y=0)