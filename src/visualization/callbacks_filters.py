from dash import Input, Output
import pandas as pd


def register_filter_callbacks(app, dashboard_instance):
    """
    Register filter and selector callbacks.
    
    Args:
        app: Dash app instance
        dashboard_instance: TranslationDashboard instance
    """
    
    @app.callback(
        Output('agent-selector', 'options'),
        Input('interval-component', 'n_intervals')
    )
    def update_agent_options(n):
        """Update agent dropdown options."""
        data = dashboard_instance._load_data()
        if data.empty or 'agent_type' not in data.columns:
            return []
        agents = data['agent_type'].unique()
        return [{'label': agent, 'value': agent} for agent in sorted(agents)]


def filter_data(data: pd.DataFrame, selected_agents, error_range):
    """
    Apply filters to data.
    
    Args:
        data: Input DataFrame
        selected_agents: List of selected agent types
        error_range: [min, max] error rate range (0-50)
        
    Returns:
        Filtered DataFrame
    """
    filtered = data.copy()
    if selected_agents:
        filtered = filtered[filtered['agent_type'].isin(selected_agents)]
    
    error_min, error_max = error_range[0] / 100, error_range[1] / 100
    filtered = filtered[
        (filtered['error_rate_target'] >= error_min) &
        (filtered['error_rate_target'] <= error_max)
    ]
    
    return filtered

