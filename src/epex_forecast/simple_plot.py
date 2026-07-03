import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_forecast(forecast_df: pd.DataFrame, meta: dict = None):
    forecat_columns = [col for col in forecast_df.columns if col != "ground truth"]
    plt.figure(figsize=(12, 5))

    if len(forecat_columns) > 1:
        assert len(forecat_columns) % 2 == 1 # only odd number of quantiles (paarwise + one main forecast)

        main_id = len(forecat_columns) // 2 # center quantile = main forecast
        main_col = forecat_columns[main_id]

        color_alphas = np.linspace(0, 0.15, main_id+1, endpoint=True)[1:]
        for i in range(main_id):
            lower_col = forecat_columns[i]
            upper_col = forecat_columns[-i - 1]
            plt.fill_between(forecast_df.index, forecast_df[lower_col], forecast_df[upper_col], color="blue", alpha=color_alphas[i])
        plt.plot(forecast_df.index, forecast_df[main_col], label="forecast", color="blue", linewidth=3, alpha=0.7)

    plt.plot(forecast_df.index, forecast_df["ground truth"], label="ground truth", color="red", linewidth=3, alpha=0.8)
    plt.xlim(forecast_df.index[0], forecast_df.index[-1])
    plt.grid()
    plt.xlabel("Time")
    plt.ylabel("Price / €/MWh")
    plt.title("Forecast for " + meta["region"]) if meta is not None else None
    plt.legend(loc="best")
    plt.show()
