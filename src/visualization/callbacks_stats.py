from dash import Input, Output, html


def register_stats_callbacks(app, dashboard_instance):
    """
    Register summary statistics callbacks.
    
    Args:
        app: Dash app instance
        dashboard_instance: TranslationDashboard instance
    """
    
    @app.callback(
        [Output('summary-stats', 'children'),
         Output('experiment-details', 'children')],
        [Input('agent-selector', 'value'),
         Input('error-rate-slider', 'value'),
         Input('interval-component', 'n_intervals')]
    )
    def update_stats(selected_agents, error_range, n):
        """Update summary statistics."""
        data = dashboard_instance._load_data()
        
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

