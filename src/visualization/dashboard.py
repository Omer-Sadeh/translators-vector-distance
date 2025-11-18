import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional
from pathlib import Path

from src.data.storage import ExperimentStorage
from src.config import get_settings


class TranslationDashboard:
    """
    Interactive Plotly Dash dashboard for experiment visualization.
    
    Provides real-time exploration of translation quality experiments
    with interactive controls and multiple visualization types.
    """
    
    def __init__(
        self,
        storage: ExperimentStorage,
        host: str = '127.0.0.1',
        port: int = 8050
    ):
        """
        Initialize dashboard.
        
        Args:
            storage: ExperimentStorage instance
            host: Dashboard host
            port: Dashboard port
        """
        self.storage = storage
        self.host = host
        self.port = port
        
        self.app = dash.Dash(
            __name__,
            title='Translation Vector Distance Analysis'
        )
        
        self._setup_layout()
        self._setup_callbacks()
    
    def _load_data(self) -> pd.DataFrame:
        """Load data from storage."""
        results = self.storage.get_all_results()
        if not results:
            return pd.DataFrame()
        return pd.DataFrame(results)
    
    def _setup_layout(self):
        """Setup dashboard layout."""
        self.app.layout = html.Div([
            html.H1(
                'Translation Chain Vector Distance Analysis',
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}
            ),
            
            html.Div([
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
            ], style={'marginBottom': 30}),
            
            html.Div([
                html.Div([
                    html.H3('Summary Statistics', style={'color': '#34495e'}),
                    html.Div(id='summary-stats')
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                
                html.Div([
                    html.H3('Experiment Details', style={'color': '#34495e'}),
                    html.Div(id='experiment-details')
                ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%', 'verticalAlign': 'top'})
            ], style={'marginBottom': 30}),
            
            html.Div([
                dcc.Graph(id='error-distance-plot')
            ], style={'marginBottom': 30}),
            
            html.Div([
                html.Div([
                    dcc.Graph(id='distribution-plot')
                ], style={'width': '48%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(id='agent-comparison-plot')
                ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
            ], style={'marginBottom': 30}),
            
            html.Div([
                dcc.Graph(id='scatter-plot')
            ]),
            
            dcc.Interval(
                id='interval-component',
                interval=10*1000,
                n_intervals=0
            )
        ], style={'padding': 30, 'fontFamily': 'Arial, sans-serif'})
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks."""
        
        @self.app.callback(
            Output('agent-selector', 'options'),
            Input('interval-component', 'n_intervals')
        )
        def update_agent_options(n):
            data = self._load_data()
            if data.empty or 'agent_type' not in data.columns:
                return []
            agents = data['agent_type'].unique()
            return [{'label': agent, 'value': agent} for agent in sorted(agents)]
        
        @self.app.callback(
            [Output('summary-stats', 'children'),
             Output('experiment-details', 'children')],
            [Input('agent-selector', 'value'),
             Input('error-rate-slider', 'value'),
             Input('interval-component', 'n_intervals')]
        )
        def update_stats(selected_agents, error_range, n):
            data = self._load_data()
            
            if data.empty:
                return 'No data available', 'No experiments found'
            
            filtered = data.copy()
            if selected_agents:
                filtered = filtered[filtered['agent_type'].isin(selected_agents)]
            
            error_min, error_max = error_range[0] / 100, error_range[1] / 100
            filtered = filtered[
                (filtered['error_rate_target'] >= error_min) &
                (filtered['error_rate_target'] <= error_max)
            ]
            
            if filtered.empty:
                return 'No data for selection', 'Adjust filters'
            
            stats_div = html.Div([
                html.P(f"Total Experiments: {len(filtered)}"),
                html.P(f"Successful: {filtered['success'].sum()} ({filtered['success'].mean():.1%})"),
                html.P(f"Mean Cosine Distance: {filtered['cosine_distance'].mean():.4f}"),
                html.P(f"Std Cosine Distance: {filtered['cosine_distance'].std():.4f}")
            ])
            
            details_div = html.Div([
                html.P(f"Agents: {filtered['agent_type'].nunique()}"),
                html.P(f"Error Rates Tested: {filtered['error_rate_target'].nunique()}"),
                html.P(f"Unique Sentences: {filtered['sentence_id'].nunique()}"),
                html.P(f"Avg Duration: {filtered['duration_seconds'].mean():.1f}s")
            ])
            
            return stats_div, details_div
        
        @self.app.callback(
            Output('error-distance-plot', 'figure'),
            [Input('agent-selector', 'value'),
             Input('error-rate-slider', 'value'),
             Input('interval-component', 'n_intervals')]
        )
        def update_error_distance_plot(selected_agents, error_range, n):
            data = self._load_data()
            
            if data.empty:
                return go.Figure().add_annotation(text="No data available")
            
            filtered = data.copy()
            if selected_agents:
                filtered = filtered[filtered['agent_type'].isin(selected_agents)]
            
            error_min, error_max = error_range[0] / 100, error_range[1] / 100
            filtered = filtered[
                (filtered['error_rate_target'] >= error_min) &
                (filtered['error_rate_target'] <= error_max)
            ]
            
            if filtered.empty:
                return go.Figure().add_annotation(text="No data for selection")
            
            grouped = filtered.groupby('error_rate_target')['cosine_distance'].agg(['mean', 'std', 'count'])
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=grouped.index * 100,
                y=grouped['mean'],
                mode='lines+markers',
                name='Mean Distance',
                line=dict(width=3),
                marker=dict(size=10)
            ))
            
            ci = 1.96 * grouped['std'] / np.sqrt(grouped['count'])
            fig.add_trace(go.Scatter(
                x=grouped.index * 100,
                y=grouped['mean'] + ci,
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=grouped.index * 100,
                y=grouped['mean'] - ci,
                mode='lines',
                line=dict(width=0),
                fillcolor='rgba(68, 68, 68, 0.3)',
                fill='tonexty',
                name='95% CI'
            ))
            
            fig.update_layout(
                title='Error Rate vs Cosine Distance',
                xaxis_title='Spelling Error Rate (%)',
                yaxis_title='Cosine Distance',
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
        
        @self.app.callback(
            Output('distribution-plot', 'figure'),
            [Input('agent-selector', 'value'),
             Input('error-rate-slider', 'value'),
             Input('interval-component', 'n_intervals')]
        )
        def update_distribution_plot(selected_agents, error_range, n):
            data = self._load_data()
            
            if data.empty:
                return go.Figure().add_annotation(text="No data available")
            
            filtered = data.copy()
            if selected_agents:
                filtered = filtered[filtered['agent_type'].isin(selected_agents)]
            
            error_min, error_max = error_range[0] / 100, error_range[1] / 100
            filtered = filtered[
                (filtered['error_rate_target'] >= error_min) &
                (filtered['error_rate_target'] <= error_max)
            ]
            
            if filtered.empty:
                return go.Figure().add_annotation(text="No data for selection")
            
            filtered['error_rate_pct'] = (filtered['error_rate_target'] * 100).astype(int).astype(str) + '%'
            
            fig = px.box(
                filtered,
                x='error_rate_pct',
                y='cosine_distance',
                title='Distance Distribution by Error Rate',
                labels={'error_rate_pct': 'Error Rate', 'cosine_distance': 'Cosine Distance'}
            )
            
            fig.update_layout(template='plotly_white')
            
            return fig
        
        @self.app.callback(
            Output('agent-comparison-plot', 'figure'),
            [Input('agent-selector', 'value'),
             Input('error-rate-slider', 'value'),
             Input('interval-component', 'n_intervals')]
        )
        def update_agent_comparison(selected_agents, error_range, n):
            data = self._load_data()
            
            if data.empty or 'agent_type' not in data.columns:
                return go.Figure().add_annotation(text="No data available")
            
            error_min, error_max = error_range[0] / 100, error_range[1] / 100
            filtered = data[
                (data['error_rate_target'] >= error_min) &
                (data['error_rate_target'] <= error_max)
            ]
            
            if filtered.empty:
                return go.Figure().add_annotation(text="No data for selection")
            
            agent_means = filtered.groupby('agent_type')['cosine_distance'].mean().sort_values()
            
            fig = go.Figure(data=[
                go.Bar(x=agent_means.index, y=agent_means.values)
            ])
            
            fig.update_layout(
                title='Agent Performance Comparison',
                xaxis_title='Agent Type',
                yaxis_title='Mean Cosine Distance',
                template='plotly_white'
            )
            
            return fig
        
        @self.app.callback(
            Output('scatter-plot', 'figure'),
            [Input('agent-selector', 'value'),
             Input('error-rate-slider', 'value'),
             Input('interval-component', 'n_intervals')]
        )
        def update_scatter_plot(selected_agents, error_range, n):
            data = self._load_data()
            
            if data.empty:
                return go.Figure().add_annotation(text="No data available")
            
            filtered = data.copy()
            if selected_agents:
                filtered = filtered[filtered['agent_type'].isin(selected_agents)]
            
            error_min, error_max = error_range[0] / 100, error_range[1] / 100
            filtered = filtered[
                (filtered['error_rate_target'] >= error_min) &
                (filtered['error_rate_target'] <= error_max)
            ]
            
            if filtered.empty:
                return go.Figure().add_annotation(text="No data for selection")
            
            fig = px.scatter(
                filtered,
                x='error_rate_actual',
                y='cosine_distance',
                color='agent_type',
                hover_data=['translation_en'],
                title='Error Rate vs Distance (All Experiments)',
                labels={
                    'error_rate_actual': 'Actual Error Rate',
                    'cosine_distance': 'Cosine Distance',
                    'agent_type': 'Agent'
                }
            )
            
            fig.update_layout(template='plotly_white')
            
            return fig
    
    def run(self, debug: bool = False):
        """
        Run the dashboard server.
        
        Args:
            debug: Enable debug mode
        """
        self.app.run_server(host=self.host, port=self.port, debug=debug)


def create_dashboard(config_path: Optional[str] = None) -> TranslationDashboard:
    """
    Create dashboard instance from configuration.
    
    Args:
        config_path: Optional configuration file path
        
    Returns:
        TranslationDashboard instance
    """
    settings = get_settings(config_path)
    storage = ExperimentStorage(settings.get_database_path())
    
    host = settings.get('dashboard.host', '127.0.0.1')
    port = settings.get('dashboard.port', 8050)
    
    return TranslationDashboard(storage, host, port)

