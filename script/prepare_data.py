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
import pandas as pd


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
	encoding="utf-8"
)

df_volume = pd.read_csv(
	f"{DIR_DATA}volume.tsv",
	sep="\t",
	header=0,
	index_col=0,
	encoding="utf-8"
)

df_announcement = pd.read_csv(
	f"{DIR_DATA}announcement.tsv",
	sep="\t",
	header=0,
	index_col=0,
	encoding="utf-8"
)


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
