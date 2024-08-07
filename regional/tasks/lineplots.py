#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Plot departamental rates with lines
"""
import pandas
import matplotlib.pyplot as plt
import seaborn


# + tags=[]
def by_quinquennio(product, upstream, rates_over):
    # 1. read the data
    df = pandas.read_parquet(upstream['get_quinquenial']['data'])
    #df = pandas.read_parquet('../_products/rates/rates-by-quinquenios.parquet')

    # 2. pivot dataframe (regions x periods)
    cols = ['periodo', 'region_nombre', 'tasa']
    df_periodos = df[cols].pivot(index='periodo', columns='region_nombre')
    df_periodos.index.name = None
    df_periodos.columns = pandas.Index([c for _, c in df_periodos.columns])

    # 3. create figure
    f, ax = plt.subplots(figsize=(12, 8))
    custom_params = {"axes.spines.right": False, "axes.spines.top": False}
    seaborn.set_theme(style="whitegrid", rc=custom_params)
    seaborn.lineplot(data=df_periodos)
    ax.set_xlabel('Quinquenio', fontsize=14)
    ax.set_ylabel('Tasa', fontsize=14)
    f.suptitle(
        f"Tasas de mortinatos por cada {rates_over} nacimientos (1994-2019)",
        fontsize=16)
    plt.savefig(str(product), dpi=300)
    plt.close()


# + tags=[]
def by_years(product, upstream, rates_over):
    # 1. read the data
    df = pandas.read_parquet(upstream['get_annual']['data'])
    #df = pandas.read_parquet('../_products/rates/rates-by-year.parquet')

    # 2. pivot dataframe (regions x periods)
    cols = ['año', 'region_nombre', 'tasa']
    df_periodos = df[cols].pivot(index='año', columns='region_nombre')
    df_periodos.index.name = None
    df_periodos.columns = pandas.Index([c for _, c in df_periodos.columns])

    # 3. create figure
    f, ax = plt.subplots(figsize=(12, 8))
    custom_params = {"axes.spines.right": False, "axes.spines.top": False}
    seaborn.set_theme(style="whitegrid", rc=custom_params)
    line_plot = seaborn.lineplot(data=df_periodos, ax=ax)
    line_plot.set_xlabel('Año')
    line_plot.set_ylabel('Tasa')
    fig = line_plot.get_figure()
    fig.suptitle(f"Tasas de mortinatos por cada {rates_over} nacimientos (1994-2019)", fontsize=16)
    fig.savefig(str(product), dpi=300)
    plt.close()
