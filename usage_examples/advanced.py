from epex_forecast import EPEXForecasterClient, plot_forecast

# ------ create API client ---------------------------------------------------------------
# your API key goes here, for testing purposes a public demo key is used
your_private_token = "demo_token_0bf049bd50427104c2cbaf51031a3f7864858b27"

client = EPEXForecasterClient(api_key=your_private_token)


# ------ get forecast ----------------------------------------------------------------------
forecast_df, meta = client.get_forecast(
    from_time="2026-06-10T18:05:42Z",   # individual start and end times
    to_time="2026-08-02T00:00:00Z",
    market="AT",    # define market (choose from list)
    model_id="Chr2-prob-7step-[96]" # choose individual model
)


# ------ plot forecast ---------------------------------------------------------------------
plot_forecast(forecast_df, meta)
