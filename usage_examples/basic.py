from epex_forecast import EPEXForecasterClient, plot_forecast

# create API client
client = EPEXForecasterClient()

# get forecast
forecast_df, meta = client.get_forecast()

# plot
plot_forecast(forecast_df, meta)



