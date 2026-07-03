import pandas as pd
import requests
from datetime import datetime, timedelta

from default_settings import DEFAULT_BACKEND_URL, DEFAULT_MARKET
from epex_forecast.simple_plot import plot_forecast


def _query_api(
        from_time: str,
        to_time: str,
        series: str,
        market: str,
        url: str,
        model_id: str
):
    params = {
        "from": from_time,
        "to": to_time,
        "series": series,
        "market": market
    }
    if model_id is not None:
        params["model_id"] = model_id

    headers = {
        "accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    return response.json()


def convert_ts_to_df(response: dict):
    assert "data" in response
    assert "meta" in response

    def _replace_nan_rows(forecast_values):
        no_forecasts = None
        for entry in forecast_values:
            if entry is not None:
                no_forecasts = len(entry)
                break
        if no_forecasts is None:
            raise ValueError("No forecast values found")

        forecast_values = [val if val is not None else [None] * no_forecasts for val in forecast_values]
        return forecast_values

    data = response["data"]

    times = []
    market_values = []
    forecast_values = []
    for timepoint_entry in data:
        times.append(timepoint_entry["ts"])
        market_values.append(timepoint_entry["market"])
        forecast_values.append(timepoint_entry["forecast"])

    forecast_values = _replace_nan_rows(forecast_values)

    data_df = pd.DataFrame(data={f"ground truth": market_values}, index=times)
    forecast_df = pd.DataFrame(data=forecast_values, index=times)
    data_df.index = pd.DatetimeIndex(data_df.index)
    forecast_df.index = pd.DatetimeIndex(forecast_df.index)

    merged_df = pd.concat([data_df, forecast_df], axis=1)

    return merged_df


def get_epex_forecast(
        from_time: str = None,
        to_time: str = None,
        series: str = None,
        market: str = None,
        backend_url: str = None,
        model_id: str = None
):
    if from_time is None and to_time is None:
        from_time = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        to_time = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")

    if series is None:
        series = "market,forecast"

    if market is None:
        market = DEFAULT_MARKET

    if backend_url is None:
        backend_url = DEFAULT_BACKEND_URL

    response = _query_api(from_time, to_time, series, market, backend_url, model_id)
    return convert_ts_to_df(response), response["meta"]


if __name__ == "__main__":
    forecast_df, meta = get_epex_forecast()
    plot_forecast(forecast_df, meta)
