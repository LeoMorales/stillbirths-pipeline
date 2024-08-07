#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Plot departamental rates by years
"""
import pandas
from pandas_profiling import ProfileReport

# + tags=["parameters"]
upstream = ["get_annual"]
product = None

# + [markdown] tags=[]
# # Leer tasas

# + tags=[]
#df = pandas.read_parquet(upstream['get_annual']['data'])
df = pandas.read_parquet('../_products/rates/rates-by-year.parquet')
# -

df.head()

df.nacimientos.sum()

df.fallecimientos.sum()

# # Profile

ProfileReport(df, title="Annual Rates Data Profiling Report")


