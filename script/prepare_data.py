# %%
"""
Name: prepare_data.py
Created by: Masato Shima
Created on: 2020/10/16
Description:
"""

# %%
# **************************************************
# ----- Import Library
# **************************************************
import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# %%
# **************************************************
# ----- Constant & Variables
# **************************************************
DIR_DATA = "./../data/"


# %%
# **************************************************
# ----- load_data
# **************************************************
df_price = pd.read_csv(
	f"{DIR_DATA}price.tsv",
	sep="\t",
	header=0,
	index_col=0,
	encoding="utf-8",
	parse_dates=True
)

df_volume = pd.read_csv(
	f"{DIR_DATA}volume.tsv",
	sep="\t",
	header=0,
	index_col=0,
	encoding="utf-8",
	parse_dates=True
)

df_announcement = pd.read_csv(
	f"{DIR_DATA}announcement.tsv",
	sep="\t",
	header=0,
	index_col=None,
	encoding="utf-8"
)

df_beta_topix = pd.read_csv(
	f"{DIR_DATA}beta_topix.tsv",
	sep="\t",
	header=0,
	index_col=0,
	encoding="utf-8",
	parse_dates=True
)

df_beta_nk225 = pd.read_csv(
	f"{DIR_DATA}beta_nk225.tsv",
	sep="\t",
	header=0,
	index_col=0,
	encoding="utf-8",
	parse_dates=True
)


# %%
# **************************************************
# ----- Resample to weekly price data
# **************************************************
df_price_weekly = df_price.groupby(pd.Grouper(level=0, freq="W"))
df_price_weekly_first = df_price_weekly.first()
df_price_weekly_last = df_price_weekly.last()


# %%
# **************************************************
# ----- Aggregate announcement data
# **************************************************
df_announcement["決算発表日"] = pd.to_datetime(df_announcement["決算発表日"])

df_announcement_weekly = df_announcement.groupby(pd.Grouper(key="決算発表日", freq="W"))
df_announcement_weekly = pd.DataFrame(
	{
		"date": df_announcement_weekly.count().index.tolist(),
		"count": df_announcement_weekly.count()["銘柄コード"].values.tolist()
	}
)

sns.set()
sns.relplot(
	data=df_announcement_weekly,
	x="date",
	y="count",
	kind="line",
	height=10,
	aspect=1.618
)

plt.show()


# %%
# **************************************************
# ----- Exploring earnings season
# **************************************************
# season の列を新規に作成し, 決算発表を行う銘柄が
# 一定件数以上の週の行を True, 一定件数以下の週の行を False,
# とする
for index, row in df_announcement_weekly.iterrows():
	if row["count"] >= 100:
		df_announcement_weekly.at[index, "season"] = True
	else:
		df_announcement_weekly.at[index, "season"] = False

# %%
# 決算シーズンの最初の週を探索
df_earnings_season_start_weeks = df_announcement_weekly[
	(df_announcement_weekly["season"] != df_announcement_weekly["season"].shift(1)) &
	(df_announcement_weekly["season"] == 1)
]

df_earnings_season_start_weeks.reset_index(drop=True, inplace=True)


# %%
# **************************************************
# ----- Back test
# **************************************************
for _, row in df_earnings_season_start_weeks.iterrows():
	date = row["date"]
	date = datetime.datetime.strftime(date, "%Y/%m/%d")

	i = 1

	while True:
		try:
			stocks: pd.Series
			stocks = df_beta_topix.loc[date]
			break
		except KeyError:
			date = datetime.datetime.strptime(date, "%Y/%m/%d")
			date = date + datetime.timedelta(days=i)
			date = datetime.datetime.strftime(date, "%Y/%m/%d")
			i += 1

	stocks.dropna(inplace=True)
	stocks.sort_values(ascending=False, inplace=True)
	stocks = stocks[:30].index.tolist()

	price_first = df_price_weekly_first.loc[row["date"], stocks]
	price_last = df_price_weekly_last.loc[row["date"], stocks]


# %%
# # **************************************************
# # ----- Main
# # **************************************************
# if __name__ == "__main__":
#
# 	main()

# **************************************************
# ----- End
# **************************************************
