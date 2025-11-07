import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import re

# Load and preprocess data
def load_data():
    # Create sample data since we don't have the CSV file
    # In production, you'd load from: df = pd.read_csv('allen_sales.csv')
    data = {
        'Close Price': [417500, 434000, 445000, 455000, 425000, 494150, 478500, 500000, 500000, 454000,
                       497500, 431990, 487000, 475000, 479000, 525000, 530000, 550000, 530000, 515000,
                       520000, 475000, 600000, 635000, 582000, 525000, 599900, 675000],
        'SqFt': [1592, 1783, 1946, 1946, 2007, 2222, 2265, 2470, 2470, 2471,
                 2471, 2476, 2477, 2492, 2512, 2875, 2875, 2875, 2876, 2986,
                 3007, 3062, 3080, 3080, 3118, 3135, 3368, 3908],
        'Acres': [0.126, 0.190, 0.174, 0.210, 0.130, 0.273, 0.150, 0.130, 0.180, 0.130,
                  0.130, 0.130, 0.200, 0.130, 0.130, 0.220, 0.210, 0.240, 0.200, 0.170,
                  0.180, 0.210, 0.210, 0.220, 0.220, 0.200, 0.200, 0.270],
        'Year Built': [1999, 1998, 1999, 2000, 2000, 2000, 2001, 1999, 1999, 1998,
                       1999, 1999, 1999, 1999, 1999, 1998, 2000, 1999, 2000, 1999,
                       2000, 2001, 2001, 2001, 1999, 1999, 2000, 1999],
        'Beds Total': [3, 3, 4, 4, 4, 4, 4, 5, 4, 4, 5, 5, 4, 4, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 5, 5],
        'Bath Full': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 2, 2, 2, 3, 2, 2, 3, 2, 4],
        'Baths Half': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0],
        'Pool YN': ['No', 'No', 'Yes', 'No', 'No', 'Yes', 'No', 'No', 'No', 'No',
                    'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No',
                    'No', 'No', 'No', 'No', 'Yes', 'No', 'Yes', 'No'],
        'Elementary School Name': ['Anderson', 'Anderson', 'Anderson', 'Anderson', 'Olson', 'Olson', 'Olson', 'Olson', 'Anderson', 'Olson',
                                   'Olson', 'Vaughan', 'Olson', 'Anderson', 'Vaughan', 'Olson', 'Olson', 'Olson', 'Olson', 'Anderson',
                                   'Olson', 'Anderson', 'Olson', 'Olson', 'Olson', 'Olson', 'Olson', 'Anderson'],
        'Address': ['1532 Fallcreek Court', '104 N Alder Drive', '1424 Winterwood Drive', '211 Windsong Way', '1522 Broadmoor Drive',
                    '215 Sunridge Way', '203 Northaven Drive', '1520 Fallcreek Court', '1519 Autumnmist Drive', '104 Sunridge Way',
                    '1509 Fallcreek Court', '302 Trailwood Drive', '108 Southpoint Court', '309 Trailwood Drive', '302 Trailwood Drive',
                    '111 Southpoint Court', '1432 Stillforest Drive', '102 Southpoint Court', '1426 Autumnmist Drive', '1417 Winterwood Drive',
                    '210 Windsong Way', '414 Leameadow Drive', '1429 Stillforest Drive', '1426 Fieldstone Drive', '1401 Stillforest Drive',
                    '1403 Sweet Gum Drive', '1427 Fieldstone Drive', '1401 Fieldstone Drive']
    }
    
    df = pd.DataFrame(data)
    df['Total Baths'] = df['Bath Full'] + (df['Baths Half'] / 2)
    
    # Extract subdivision from address
    def extract_subdivision(address):
        if 'Fallcreek' in address: return 'Fallcreek'
        if 'Winterwood' in address: return 'Winterwood'
        if 'Windsong' in address: return 'Windsong'
        if 'Broadmoor' in address: return 'Broadmoor'
        if 'Northaven' in address: return 'Northaven'
        if 'Autumnmist' in address: return 'Autumnmist'
        if 'Sunridge' in address: return 'Sunridge'
        if 'Stillforest' in address: return 'Stillforest'
        if 'Fieldstone' in address: return 'Fieldstone'
        if 'Trailwood' in address: return 'Trailwood'
        if 'Alder' in address: return 'Alder Heights'
        if 'Southpoint' in address: return 'Southpoint'
        if 'Leameadow' in address: return 'Leameadow'
        if 'Sweet Gum' in address: return 'Sweet Gum'
        return 'Unknown'
    
    df['Subdivision'] = df['Address'].apply(extract_subdivision)
    
    return df

df = load_data()

# Calculate ranges for sliders
min_sqft, max_sqft = int(df['SqFt'].min()), int(df['SqFt'].max())
min_year, max_year = int(df['Year Built'].min()), int(df['Year Built'].max())
min_beds, max_beds = int(df['Beds Total'].min()), int(df['Beds Total'].max())
min_baths, max_baths = float(df['Total Baths'].min()), float(df['Total Baths'].max())
min_price, max_price = int(df['Close Price'].min()), int(df['Close Price'].max())

# Initialize app with modern theme
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Allen, TX Property Market Explorer"

# Custom styling
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "320px",
    "padding": "2rem 1rem",
    "backgroundColor": "#2b2b2b",
    "overflowY": "auto"
}

CONTENT_STYLE = {
    "marginLeft": "320px",
    "padding": "2rem 1rem",
    "backgroundColor": "#1a1a1a"
}

# Layout
app.layout = dbc.Container([
    # Sidebar with filters
    html.Div([
        html.H2("?? Market Explorer", className="text-light mb-4"),
        html.Hr(),
        
        html.H5("Price Range", className="text-light"),
        dcc.RangeSlider(
            id='price-slider',
            min=min_price,
            max=max_price,
            value=[min_price, max_price],
            step=5000,
            marks={i: f'${i//1000}K' for i in range(min_price, max_price+1, 50000)},
            className="mb-4"
        ),
        
        html.H5("Square Feet", className="text-light"),
        dcc.RangeSlider(
            id='sqft-slider',
            min=min_sqft,
            max=max_sqft,
            value=[min_sqft, max_sqft],
            step=100,
            marks={i: f'{i//1000}K' for i in range(min_sqft, max_sqft+1, 500)},
            className="mb-4"
        ),
        
        html.H5("Year Built", className="text-light"),
        dcc.RangeSlider(
            id='year-slider',
            min=min_year,
            max=max_year,
            value=[min_year, max_year],
            step=1,
            marks={i: str(i) for i in range(min_year, max_year+1)},
            className="mb-4"
        ),
        
        html.H5("Bedrooms", className="text-light"),
        dcc.RangeSlider(
            id='beds-slider',
            min=min_beds,
            max=max_beds,
            value=[min_beds, max_beds],
            step=1,
            marks={i: str(i) for i in range(min_beds, max_beds+1)},
            className="mb-4"
        ),
        
        html.H5("Bathrooms", className="text-light"),
        dcc.RangeSlider(
            id='baths-slider',
            min=min_baths,
            max=max_baths,
            value=[min_baths, max_baths],
            step=0.5,
            marks={i: f"{i:.1f}" for i in [min_baths, max_baths]},
            className="mb-4"
        ),
        
        html.H5("Pool", className="text-light"),
        dcc.Dropdown(
            id='pool-dropdown',
            options=[
                {'label': 'All Properties', 'value': 'All'},
                {'label': 'With Pool', 'value': 'Yes'},
                {'label': 'No Pool', 'value': 'No'}
            ],
            value='All',
            className="mb-4"
        ),
        
        html.H5("Elementary School", className="text-light"),
        dcc.Dropdown(
            id='school-dropdown',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': school, 'value': school} for school in sorted(df['Elementary School Name'].unique())],
            value='All',
            className="mb-4"
        ),
        
        html.H5("Subdivision", className="text-light"),
        dcc.Dropdown(
            id='subdivision-dropdown',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': sub, 'value': sub} for sub in sorted(df['Subdivision'].unique()) if sub != 'Unknown'],
            value='All',
            className="mb-4"
        ),
        
        dbc.Button("Reset Filters", id="reset-btn", color="primary", className="w-100 mb-3"),
        
        html.Div([
            html.H5("Quick Stats", className="text-light"),
            html.Div(id='stats-box', className="text-light")
        ], className="mt-4 p-3", style={"backgroundColor": "#3b3b3b", "borderRadius": "8px"})
        
    ], style=SIDEBAR_STYLE),
    
    # Main content
    html.Div([
        html.H1("Allen, TX Property Market Dashboard", className="text-light text-center mb-4"),
        
        dbc.Tabs([
            dbc.Tab(label="?? Price Analysis", children=[
                dbc.Row([
                    dbc.Col(dcc.Graph(id='scatter-price-sqft', style={'height': '500px'}), width=12)
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='price-dist-hist', style={'height': '350px'}), width=6),
                    dbc.Col(dcc.Graph(id='avg-by-school', style={'height': '350px'}), width=6)
                ])
            ]),
            
            dbc.Tab(label="??? Neighborhood View", children=[
                dbc.Row([
                    dbc.Col(dcc.Graph(id='avg-by-subdivision', style={'height': '500px'}), width=12)
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='beds-baths-scatter', style={'height': '400px'}), width=12)
                ])
            ])
        ], className="mt-4")
        
    ], style=CONTENT_STYLE)
    
], fluid=True, style={"padding": "0px"})

# Global variables for reset
global_vars = {
    'min_price': min_price,
    'max_price': max_price,
    'min_sqft': min_sqft,
    'max_sqft': max_sqft,
    'min_year': min_year,
    'max_year': max_year,
    'min_beds': min_beds,
    'max_beds': max_beds,
    'min_baths': min_baths,
    'max_baths': max_baths
}

# Callback to update graphs
@callback(
    [Output('scatter-price-sqft', 'figure'),
     Output('price-dist-hist', 'figure'),
     Output('avg-by-school', 'figure'),
     Output('avg-by-subdivision', 'figure'),
     Output('beds-baths-scatter', 'figure'),
     Output('stats-box', 'children')],
    [Input('price-slider', 'value'),
     Input('sqft-slider', 'value'),
     Input('year-slider', 'value'),
     Input('beds-slider', 'value'),
     Input('baths-slider', 'value'),
     Input('pool-dropdown', 'value'),
     Input('school-dropdown', 'value'),
     Input('subdivision-dropdown', 'value')]
)
def update_dashboard(price_range, sqft_range, year_range, beds_range, baths_range, pool, school, subdivision):
    # Filter data
    dff = df[
        (df['Close Price'] >= price_range[0]) & (df['Close Price'] <= price_range[1]) &
        (df['SqFt'] >= sqft_range[0]) & (df['SqFt'] <= sqft_range[1]) &
        (df['Year Built'] >= year_range[0]) & (df['Year Built'] <= year_range[1]) &
        (df['Beds Total'] >= beds_range[0]) & (df['Beds Total'] <= beds_range[1]) &
        (df['Total Baths'] >= baths_range[0]) & (df['Total Baths'] <= baths_range[1])
    ]
    
    if pool != 'All':
        dff = dff[dff['Pool YN'] == pool]
    
    if school != 'All':
        dff = dff[dff['Elementary School Name'] == school]
    
    if subdivision != 'All':
        dff = dff[dff['Subdivision'] == subdivision]
    
    # Create figures
    scatter_fig = px.scatter(
        dff, x='SqFt', y='Close Price', 
        color='Year Built', size='Acres',
        hover_data=['Address', 'Beds Total', 'Total Baths', 'Pool YN'],
        title="Price vs Square Footage",
        color_continuous_scale='Viridis'
    )
    scatter_fig.update_layout(
        template='plotly_dark', 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    hist_fig = px.histogram(
        dff, x='Close Price', 
        nbins=20,
        title="Price Distribution"
    )
    hist_fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    avg_school = dff.groupby('Elementary School Name')['Close Price'].mean().reset_index().sort_values('Close Price')
    school_fig = px.bar(
        avg_school, x='Close Price', y='Elementary School Name',
        orientation='h',
        title="Avg Price by Elementary School"
    )
    school_fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    avg_sub = dff.groupby('Subdivision')['Close Price'].mean().reset_index().sort_values('Close Price')
    sub_fig = px.bar(
        avg_sub, x='Subdivision', y='Close Price',
        title="Avg Price by Subdivision"
    )
    sub_fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45
    )
    
    beds_baths_fig = px.scatter(
        dff, x='Beds Total', y='Total Baths',
        size='Close Price', color='Close Price',
        title="Bed/Bath Ratio (bubble size = price)",
        color_continuous_scale='Plasma'
    )
    beds_baths_fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Stats box
    stats = html.Div([
        html.P(f"??? Properties: {len(dff)}"),
        html.P(f"?? Avg Price: ${dff['Close Price'].mean():,.0f}"),
        html.P(f"?? Avg Size: {dff['SqFt'].mean():.0f} sqft"),
        html.P(f"?? Pools: {dff['Pool YN'].eq('Yes').sum()}"),
        html.P(f"?? Price/sqft: ${dff['Close Price'].div(dff['SqFt']).mean():.0f}")
    ])
    
    return scatter_fig, hist_fig, school_fig, sub_fig, beds_baths_fig, stats

# Reset button callback
@callback(
    [Output('price-slider', 'value'),
     Output('sqft-slider', 'value'),
     Output('year-slider', 'value'),
     Output('beds-slider', 'value'),
     Output('baths-slider', 'value'),
     Output('pool-dropdown', 'value'),
     Output('school-dropdown', 'value'),
     Output('subdivision-dropdown', 'value')],
    Input('reset-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    return [global_vars['min_price'], global_vars['max_price']], \
           [global_vars['min_sqft'], global_vars['max_sqft']], \
           [global_vars['min_year'], global_vars['max_year']], \
           [global_vars['min_beds'], global_vars['max_beds']], \
           [global_vars['min_baths'], global_vars['max_baths']], \
           'All', 'All', 'All'

# Add server variable for production
server = app.server

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
