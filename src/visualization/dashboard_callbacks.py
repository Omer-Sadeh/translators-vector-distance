from src.visualization.callbacks_filters import register_filter_callbacks
from src.visualization.callbacks_stats import register_stats_callbacks
from src.visualization.callbacks_plots import register_plot_callbacks


def register_callbacks(app, dashboard_instance):
    """
    Register all dashboard callbacks.
    
    Args:
        app: Dash app instance
        dashboard_instance: TranslationDashboard instance
    """
    register_filter_callbacks(app, dashboard_instance)
    register_stats_callbacks(app, dashboard_instance)
    register_plot_callbacks(app, dashboard_instance)

