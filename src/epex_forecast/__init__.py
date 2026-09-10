"""epex forecast - easy access to forecast backend API"""

from epex_forecast.api_access import EPEXForecasterClient
from epex_forecast.simple_plot import plot_forecast

__version__ = "0.2.1"
__all__ = ["EPEXForecasterClient", "plot_forecast", "__version__"]
