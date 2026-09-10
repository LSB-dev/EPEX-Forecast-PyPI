import logging

import pandas as pd
import requests
from datetime import datetime, timedelta

from epex_forecast.default_settings import DEFAULT_BACKEND_URL, DEFAULT_MARKET, TARGET_FORMAT, DEMO_API_KEY
from epex_forecast.simple_plot import plot_forecast


def _query_api(
        from_time: str,
        to_time: str,
        series: str,
        market: str,
        url: str,
        model_id: str,
        api_key: str,
        timeout: int
):
    params = {
        "from_time": from_time,
        "to_time": to_time,
        "series": series,
        "market": market,
        "token": api_key
    }
    if model_id is not None:
        params["model_id"] = model_id

    headers = {
        "accept": "application/json"
    }

    print(params)
    response = requests.get(url, params=params, headers=headers, timeout=timeout)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f"Request failed with status code {response.status_code}: {response.text}")

    return response.json()


def _convert_ts_to_df(response: dict):
    assert "data" in response
    assert "meta" in response

    def _replace_nan_rows(forecast_values):
        no_forecasts = None
        for entry in forecast_values:
            if entry is not None:
                no_forecasts = len(entry)
                break
        if no_forecasts is None:
            raise ValueError("No forecast values available for this request")

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

    if len(forecast_values) > 0:
        forecast_values = _replace_nan_rows(forecast_values)
    else:
        forecast_values = [None for _ in times]

    data_df = pd.DataFrame(data={f"ground truth": market_values}, index=times)
    forecast_df = pd.DataFrame(data=forecast_values, index=times)
    data_df.index = pd.DatetimeIndex(data_df.index)
    forecast_df.index = pd.DatetimeIndex(forecast_df.index)

    merged_df = pd.concat([data_df, forecast_df], axis=1)

    return merged_df


def _check_time_format(datetime_str):
    if datetime_str is not None:
        try:
            datetime.strptime(datetime_str, TARGET_FORMAT)
            return True
        except ValueError:
            raise ValueError(f"Invalid time format: {datetime_str}, make sure it is in the format {TARGET_FORMAT}")


class EPEXForecasterClient:
    def __init__(self,
                 backend_url: str = None,
                 api_key: str = None,
                 timeout: int = 10,
                 ):

        if backend_url is None:
            backend_url = DEFAULT_BACKEND_URL
        self.backend_url = backend_url

        if api_key is None:
            logging.warning("No API key provided. From Sep 2026 on, the Forecast API requires an API key to be provided. Please contact the team if you need an API key.")
            logging.warning("The default Demo-API key will be used for now - however, it has very limited usage and might be removed in the future.")
            api_key = DEMO_API_KEY

        self.api_key = api_key

        self.timeout = timeout

        # check connection
        self._check_connection()

    def _check_connection(self):
        """
        Checks:  API accessible and credentials correct.
        """

        # check overall connection
        url = f"{self.backend_url}/health"
        response = requests.get(url, timeout=self.timeout)

        response.raise_for_status()

    def get_forecast(
            self,
            from_time: str = None,
            to_time: str = None,
            series: str = None,
            market: str = None,
            model_id: str = None
    ):
        # assert input times are either None or in the correct format
        _check_time_format(from_time)
        _check_time_format(to_time)

        if from_time is None and to_time is None:
            # both not given - set both to current time
            from_time = (datetime.now() - timedelta(days=5)).strftime(TARGET_FORMAT)
            to_time = (datetime.now() + timedelta(days=2)).strftime(TARGET_FORMAT)
        elif from_time is not None and to_time is None:
            # only "to" not given - set to_time 7 days later
            from_time_object = datetime.strptime(from_time, TARGET_FORMAT)
            to_time = (from_time_object + timedelta(days=7)).strftime(TARGET_FORMAT)
        elif from_time is None and to_time is not None:
            # only "from" not given - set from_time 7 days prior
            to_time_object = datetime.strptime(to_time, TARGET_FORMAT)
            from_time = (to_time_object - timedelta(days=7)).strftime(TARGET_FORMAT)

        #assert from_time < to_time, "Make sure, that 'from_time' is before 'to_time' (requesting time intervall is not empyty). You set from_time='{}' and to_time='{}'".format(from_time, to_time)

        if series is None:
            series = "market,forecast"

        if market is None:
            market = DEFAULT_MARKET

        query_api = "{}/query".format(self.backend_url)

        response = _query_api(from_time, to_time, series, market, query_api, model_id, self.api_key, self.timeout)
        return _convert_ts_to_df(response), response["meta"]


if __name__ == "__main__":

    # create API client
    client = EPEXForecasterClient()

    # get forecast
    forecast_df, meta = client.get_forecast()

    # plot
    plot_forecast(forecast_df, meta)
