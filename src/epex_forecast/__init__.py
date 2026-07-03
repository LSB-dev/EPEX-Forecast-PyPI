"""epex forecast - easy access to forecast backend API"""

from epex_forecast.api_access import get_epex_forecast
from epex_forecast.simple_plot import plot_forecast

__version__ = "0.1.0"
__all__ = ["get_epex_forecast", "plot_forecast", "__version__"]
