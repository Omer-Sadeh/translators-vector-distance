from dash import dcc, html


def create_header():
    """Create dashboard header."""
    return html.H1(
        'Translation Chain Vector Distance Analysis',
        style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}
    )


def create_filters():
    """Create filter controls section."""
    return html.Div([
        html.Div([
            html.Label('Select Agent:', style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='agent-selector',
                multi=True,
                placeholder='Select agent(s)...'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%'}),
        
        html.Div([
            html.Label('Error Rate:', style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='error-rate-slider',
                min=0,
                max=50,
                step=5,
                value=[0, 50],
                marks={i: f'{i}%' for i in range(0, 51, 10)}
            )
        ], style={'width': '64%', 'display': 'inline-block'})
    ], style={'marginBottom': 30})


def create_summary_section():
    """Create summary statistics section."""
    return html.Div([
        html.Div([
            html.H3('Summary Statistics', style={'color': '#34495e'}),
            html.Div(id='summary-stats')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.H3('Experiment Details', style={'color': '#34495e'}),
            html.Div(id='experiment-details')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%', 'verticalAlign': 'top'})
    ], style={'marginBottom': 30})


def create_main_plot():
    """Create main error vs distance plot."""
    return html.Div([
        dcc.Graph(id='error-distance-plot')
    ], style={'marginBottom': 30})


def create_secondary_plots():
    """Create secondary visualization plots."""
    return html.Div([
        html.Div([
            dcc.Graph(id='distribution-plot')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='agent-comparison-plot')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
    ], style={'marginBottom': 30})


def create_scatter_plot():
    """Create scatter plot section."""
    return html.Div([
        dcc.Graph(id='scatter-plot')
    ])


def create_refresh_interval():
    """Create auto-refresh interval component."""
    return dcc.Interval(
        id='interval-component',
        interval=10*1000,
        n_intervals=0
    )


def create_layout():
    """
    Create complete dashboard layout.
    
    Returns:
        Dash HTML layout component
    """
    return html.Div([
        create_header(),
        create_filters(),
        create_summary_section(),
        create_main_plot(),
        create_secondary_plots(),
        create_scatter_plot(),
        create_refresh_interval()
    ], style={'padding': 30, 'fontFamily': 'Arial, sans-serif'})

