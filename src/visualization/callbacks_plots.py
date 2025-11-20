from dash import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

from src.visualization.callbacks_filters import filter_data


def register_plot_callbacks(app, dashboard_instance):
    """
    Register plot update callbacks.
    
    Args:
        app: Dash app instance
        dashboard_instance: TranslationDashboard instance
    """
    
    @app.callback(
        Output('error-distance-plot', 'figure'),
        [Input('agent-selector', 'value'),
         Input('error-rate-slider', 'value'),
         Input('interval-component', 'n_intervals')]
    )
    def update_error_distance_plot(selected_agents, error_range, n):
        """Update error rate vs distance plot."""
        data = dashboard_instance._load_data()
        
        if data.empty:
            return go.Figure().add_annotation(text="No data available")
        
        filtered = filter_data(data, selected_agents, error_range)
        
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
    
    @app.callback(
        Output('distribution-plot', 'figure'),
        [Input('agent-selector', 'value'),
         Input('error-rate-slider', 'value'),
         Input('interval-component', 'n_intervals')]
    )
    def update_distribution_plot(selected_agents, error_range, n):
        """Update distance distribution plot."""
        data = dashboard_instance._load_data()
        
        if data.empty:
            return go.Figure().add_annotation(text="No data available")
        
        filtered = filter_data(data, selected_agents, error_range)
        
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
    
    @app.callback(
        Output('agent-comparison-plot', 'figure'),
        [Input('agent-selector', 'value'),
         Input('error-rate-slider', 'value'),
         Input('interval-component', 'n_intervals')]
    )
    def update_agent_comparison(selected_agents, error_range, n):
        """Update agent comparison plot."""
        data = dashboard_instance._load_data()
        
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
    
    @app.callback(
        Output('scatter-plot', 'figure'),
        [Input('agent-selector', 'value'),
         Input('error-rate-slider', 'value'),
         Input('interval-component', 'n_intervals')]
    )
    def update_scatter_plot(selected_agents, error_range, n):
        """Update scatter plot."""
        data = dashboard_instance._load_data()
        
        if data.empty:
            return go.Figure().add_annotation(text="No data available")
        
        filtered = filter_data(data, selected_agents, error_range)
        
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

