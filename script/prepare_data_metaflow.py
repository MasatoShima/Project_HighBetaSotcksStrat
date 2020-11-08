# %%
"""
Name: prepare_data_metaflow.py
Created by: Masato Shima
Created on: 2020/11/08
Description:
"""

# **************************************************
# ----- Import Library
# **************************************************
import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from metaflow import FlowSpec, step


# **************************************************
# ----- Constant & Variables
# **************************************************
DIR_DATA = "./../data/"


# **************************************************
# ----- Flow
# **************************************************
class Flow(FlowSpec):

	# **************************************************
	# ----- Start
	# **************************************************
	@step
	def start(self):
		print("Flow start")
		self.next(self.load_data)

	# **************************************************
	# ----- load_data
	# **************************************************
	@step
	def load_data(self):
		self.df_price = pd.read_csv(
			f"{DIR_DATA}price.tsv",
			sep="\t",
			header=0,
			index_col=0,
			encoding="utf-8",
			parse_dates=True
		)

		self.df_volume = pd.read_csv(
			f"{DIR_DATA}volume.tsv",
			sep="\t",
			header=0,
			index_col=0,
			encoding="utf-8",
			parse_dates=True
		)

		self.df_announcement = pd.read_csv(
			f"{DIR_DATA}announcement.tsv",
			sep="\t",
			header=0,
			index_col=None,
			encoding="utf-8"
		)

		self.df_beta_topix = pd.read_csv(
			f"{DIR_DATA}beta_topix.tsv",
			sep="\t",
			header=0,
			index_col=0,
			encoding="utf-8",
			parse_dates=True
		)

		self.df_beta_nk225 = pd.read_csv(
			f"{DIR_DATA}beta_nk225.tsv",
			sep="\t",
			header=0,
			index_col=0,
			encoding="utf-8",
			parse_dates=True
		)

		self.next(self.resample_price_weekly)

	# **************************************************
	# ----- Resample to weekly price data
	# **************************************************
	@step
	def resample_price_weekly(self):
		df_price_weekly = self.df_price.groupby(pd.Grouper(level=0, freq="W"))
		self.df_price_weekly_first = df_price_weekly.first()
		self.df_price_weekly_last = df_price_weekly.last()

		self.next(self.aggregate_announcement_data)

	# **************************************************
	# ----- Aggregate announcement data
	# **************************************************
	@step
	def aggregate_announcement_data(self):
		self.df_announcement["決算発表日"] = pd.to_datetime(self.df_announcement["決算発表日"])

		self.df_announcement_weekly = self.df_announcement.groupby(pd.Grouper(key="決算発表日", freq="W"))
		self.df_announcement_weekly = pd.DataFrame(
			{
				"date": self.df_announcement_weekly.count().index.tolist(),
				"count": self.df_announcement_weekly.count()["銘柄コード"].values.tolist()
			}
		)

		sns.set()
		sns.relplot(
			data=self.df_announcement_weekly,
			x="date",
			y="count",
			kind="line",
			height=10,
			aspect=1.618
		)

		plt.show()

		self.next(self.exploring_earnings_season)

	# **************************************************
	# ----- Exploring earnings season
	# **************************************************
	@step
	def exploring_earnings_season(self):
		# season の列を新規に作成し, 決算発表を行う銘柄が
		# 一定件数以上の週の行を True, 一定件数以下の週の行を False,
		# とする
		for index, row in self.df_announcement_weekly.iterrows():
			if row["count"] >= 100:
				self.df_announcement_weekly.at[index, "season"] = True
			else:
				self.df_announcement_weekly.at[index, "season"] = False

		# 決算シーズンの最初の週を探索
		self.df_earnings_season_start_weeks = self.df_announcement_weekly[
			(self.df_announcement_weekly["season"] != self.df_announcement_weekly["season"].shift(1)) &
			(self.df_announcement_weekly["season"] == 1)
		]

		self.df_earnings_season_start_weeks.reset_index(drop=True, inplace=True)

		self.next(self.back_test)

	# **************************************************
	# ----- Back test
	# **************************************************
	@step
	def back_test(self):
		for _, row in self.df_earnings_season_start_weeks.iterrows():
			date = row["date"]
			date = datetime.datetime.strftime(date, "%Y/%m/%d")

			i = 1

			while True:
				try:
					stocks: pd.Series
					stocks = self.df_beta_topix.loc[date]
					break
				except KeyError:
					date = datetime.datetime.strptime(date, "%Y/%m/%d")
					date = date + datetime.timedelta(days=i)
					date = datetime.datetime.strftime(date, "%Y/%m/%d")
					i += 1

			stocks.dropna(inplace=True)
			stocks.sort_values(ascending=False, inplace=True)
			stocks = stocks[:30].index.tolist()

			price_first = self.df_price_weekly_first.loc[row["date"], stocks]
			price_last = self.df_price_weekly_last.loc[row["date"], stocks]
			price_return = price_last.sum() - price_first.sum()

		self.next(self.end)

	# **************************************************
	# ----- End
	# **************************************************
	@step
	def end(self):
		print("Flow end")


# **************************************************
# ----- Main
# **************************************************
if __name__ == "__main__":

	Flow()

# **************************************************
# ----- End
# **************************************************
