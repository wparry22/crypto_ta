import pandas as pd
from ta.trend import macd, macd_signal, macd_diff
from ta.momentum import rsi
import matplotlib.pyplot as plt
import numpy as np
import cbpro
import datetime
import sys

public_client = cbpro.PublicClient()

trade_amount = 100
coins = ["BTC-USD", "ETH-USD", "ADA-USD", "UNI-USD", "BCH-USD", "LTC-USD", "LINK-USD", "XLM-USD", "MATIC-USD", "ETC-USD", "EOS-USD", "AAVE-USD", "FIL-USD", "MKR-USD", "XTZ-USD", "ATOM-USD", "ALGO-USD", "COMP-USD", "DASH-USD", "ZEC-USD", "SNX-USD", "SUSHI-USD", "YFI-USD", "MANA-USD", "BAT-USD", "ENJ-USD"]
coins = ["FIL-USD"]

current_status = pd.DataFrame()

for coin in coins:
    three_hundred_days_ago = (datetime.datetime.today().date() - datetime.timedelta(days=300)).strftime("%Y-%m-%d")
    six_hundred_days_ago = (datetime.datetime.today().date() - datetime.timedelta(days=600)).strftime("%Y-%m-%d")
    data = public_client.get_product_historic_rates(coin, granularity=86400)
    data2 =public_client.get_product_historic_rates(coin, six_hundred_days_ago, three_hundred_days_ago, granularity=86400)
    data = pd.DataFrame(data, columns=["time", "low", "high", "open", "close", "volume"])
    data2 = pd.DataFrame(data2, columns=["time", "low", "high", "open", "close", "volume"])
    data = data.append(data2)
    data["date"] = pd.to_datetime(data["time"], unit="s")

    # plt.figure(figsize=(16,6))
    # plt.plot(data["date"][:30], data["close"][:30])

    df = data[["date", "close"]][::-1]
    df["macd"] = macd(df["close"])
    df["macd_signal"] = macd_signal(df["close"])
    df["macd_diff"] = macd_diff(df["close"])
    df["rsi"] = rsi(df["close"])
    # plt.figure(figsize=(16, 6))
    # plt.plot(df["date"][-50:], df["macd"][-50:])
    # plt.plot(df["date"][-50:], df["macd_signal"][-50:])

    # plt.figure(figsize=(16,6))
    # plt.bar(df["date"][-50:], df["macd_diff"][-50:])

    # plt.figure(figsize=(16,6))
    # plt.plot(df["date"], df["rsi"])

    df2 = df.copy()
    df2 = df2.set_index("date")
    df2 = df2[["macd_diff"]]
    df2 = df2.shift(periods=1)
    main = df.merge(df2, on="date")
    conditions = [
        ((main["macd_diff_x"] < 0) & (main["macd_diff_x"] > main["macd_diff_y"])),
        ((main["macd_diff_x"] > 0) & (main["macd_diff_x"] < main["macd_diff_y"])),
        ((main["macd_diff_x"] > 0) & (main["macd_diff_y"] < 0)) | ((main["macd_diff_x"] < 0) & (main["macd_diff_y"] > 0))
    ]
    choices = ["BCONV", "SCONV", "CROSS"]
    main["today"] = np.select(conditions, choices, default="DIV")
    df4 = df.copy()
    df4 = df4.set_index("date")
    df4 = df4[["macd_diff"]]
    df4 = df4.rename(columns={"macd_diff": "macd_diff_z"})
    df4 = df4.shift(periods=2)
    main = main.merge(df4, on="date")
    conditions = [
        ((main["macd_diff_y"] < 0) & (main["macd_diff_y"] > main["macd_diff_z"])),
        ((main["macd_diff_y"] > 0) & (main["macd_diff_y"] < main["macd_diff_z"])),
        ((main["macd_diff_y"] > 0) & (main["macd_diff_z"] < 0)) | ((main["macd_diff_y"] < 0) & (main["macd_diff_z"] > 0))
    ]
    choices = ["BCONV", "SCONV", "CROSS"]
    main["yest"] = np.select(conditions, choices, default="DIV")
    df5 = df.copy()
    df5 = df5.set_index("date")
    df5 = df5[["macd_diff"]]
    df5 = df5.rename(columns={"macd_diff": "macd_diff_a"})
    df5 = df5.shift(periods=3)
    main = main.merge(df5, on="date")
    conditions = [
        ((main["macd_diff_z"] < 0) & (main["macd_diff_z"] > main["macd_diff_a"])),
        ((main["macd_diff_z"] > 0) & (main["macd_diff_z"] < main["macd_diff_a"])),
        ((main["macd_diff_z"] > 0) & (main["macd_diff_a"] < 0)) | ((main["macd_diff_z"] < 0) & (main["macd_diff_a"] > 0))
    ]
    choices = ["BCONV", "SCONV", "CROSS"]
    main["two_d_ago"] = np.select(conditions, choices, default="DIV")
    df6 = df.copy()
    df6 = df6.set_index("date")
    df6 = df6[["macd_diff"]]
    df6 = df6.rename(columns={"macd_diff": "macd_diff_b"})
    df6 = df6.shift(periods=4)
    main = main.merge(df6, on="date")
    conditions = [
        ((main["macd_diff_a"] < 0) & (main["macd_diff_a"] > main["macd_diff_b"])),
        ((main["macd_diff_a"] > 0) & (main["macd_diff_a"] < main["macd_diff_b"])),
        ((main["macd_diff_a"] > 0) & (main["macd_diff_b"] < 0)) | ((main["macd_diff_a"] < 0) & (main["macd_diff_b"] > 0))
    ]
    choices = ["BCONV", "SCONV", "CROSS"]
    main["three_d_ago"] = np.select(conditions, choices, default="DIV")
    main = main[["date", "close", "macd", "macd_signal", "macd_diff_x", "rsi", "today", "yest", "two_d_ago", "three_d_ago"]]
    main = main.rename(columns={"macd_diff_x": "macd_diff"})
    future_price = df.copy()
    future_price = future_price.set_index("date")
    future_price = future_price.shift(periods=-7)
    future_price = future_price[["close"]]
    main = main.merge(future_price, on="date")
    main = main.rename(columns={"close_x": "close", "close_y": "future_price"})
    conditions = [
        ((main["today"]=="BCONV")|(main["today"]=="CROSS"))&(main["yest"]=="BCONV"),
        (main["today"]=="CROSS")&(main["yest"]=="SCONV")
    ]
    main["action"] = np.select(conditions, ["BUY", "SELL"], "")
    remove_conseq = main.copy().set_index("date").shift(periods=1)[["action"]]
    main = main.merge(remove_conseq, on="date")
    main["action"] = np.where(main["action_x"]==main["action_y"],"",main["action_x"])
    main = main[["date", "close", "macd", "macd_signal", "macd_diff", "rsi", "today", "yest", "two_d_ago", "three_d_ago", "action"]]
    main.to_csv("main.csv")

    main_action_days = main.loc[main["action"].isin(["BUY", "SELL"])]
    remove_conseq = main_action_days.copy().set_index("date").shift(periods=1)[["action"]]
    main_action_days = main_action_days.merge(remove_conseq, on="date")
    main_action_days["action"] = np.where(main_action_days["action_x"]==main_action_days["action_y"],"",main_action_days["action_x"])
    main_action_days = main_action_days.loc[main_action_days["action"].isin(["BUY", "SELL"])]
    main_action_days["coin"] = coin
    main_action_days = main_action_days.drop(["action_x", "action_y"], axis=1)
    try:
        if main_action_days.iloc[0]["action"] == "SELL":
            main_action_days = main_action_days[1:]
    except:
        pass
    # print(main_action_days)
    buys = main_action_days.loc[main_action_days["action"]=="BUY"].reset_index()
    sells = main_action_days.loc[main_action_days["action"]=="SELL"].reset_index()
    # print(buys)
    # print(sells)
    output = buys.merge(sells, left_index=True, right_index=True)
    output = output[["coin_x", "date_x", "close_x", "date_y", "close_y"]].rename(columns={"coin_x": "coin", "date_x": "buy_date", "close_x": "buy_price", "date_y": "sell_date", "close_y": "sell_price"})
    output["profit"] = (trade_amount/output["buy_price"])*(output["sell_price"]-output["buy_price"])
    output.to_csv("output.csv")
    # print(output)
    print(coin + " PROFIT: " + str(output["profit"].sum()))
    main["coin"] = coin
    current_status = current_status.append(main[-1:])
current_status.to_csv("current_status.csv")