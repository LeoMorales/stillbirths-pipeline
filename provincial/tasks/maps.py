#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Plot departamental rates by years
"""
import pandas
import geopandas
import matplotlib.pyplot as plt
import seaborn
import os
import shutil
import pdfkit
from IPython.display import Image
import glob
import PIL


# + tags=[]
def by_years(product, upstream):

    df = pandas.read_parquet(upstream['get_annual']['data'])
    
    SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/provincias.geojson'
    shape = geopandas.read_file(SHAPE_DIR)
    shape = shape[[
        'provincia_id', 'provincia_nombre',
        'region_indec', 'geometry']]
    
    cmap = seaborn.diverging_palette(250, 5, as_cmap=True)

    ncols, nrows = 5, 7
    f, ax = plt.subplots(
        nrows=nrows, ncols=ncols,
        figsize=(20, 22),
        constrained_layout=True
    )
    axs = ax.flatten()

    for i, year_i in enumerate(sorted(list(df['año'].unique()))):
        # == Map: ==
        ax = axs[i]

        # black map background:
        shape.plot(
            ax=ax,
            color='black'
        )    
        # main map:
        pandas.merge(
            shape,
            df[df['año'] == year_i],
            on='provincia_id'
        ).plot(
            ax=ax,
            column='tasa',
            cmap=cmap,
            edgecolor='none',
            linewidth=0.02,
            legend=True,
            legend_kwds={'shrink': 0.5},
        )
        ax.axis('off')
        ax.set_title(f"Año {year_i}", fontsize=16)

    f.suptitle(
        "Tasas provinciales por año",
        fontsize=20
    )
    filled_n = ((nrows*ncols)-(i+1))  # la cantidad de celditas, menos hasta donde se llegó
    for ax_to_delete in axs[filled_n*-1:]:
        plt.delaxes(ax_to_delete)


    plt.savefig(str(product), dpi=300)
    plt.close();


# + tags=[]
def by_quinquenios(product, upstream):

    df = pandas.read_parquet(upstream['get_annual']['data'])
    
    SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/provincias.geojson'
    shape = geopandas.read_file(SHAPE_DIR)
    shape = shape[[
        'provincia_id', 'provincia_nombre',
        'region_indec', 'geometry']]
    
    cmap = seaborn.diverging_palette(250, 5, as_cmap=True)

    periods = {
        '1994-1998': [1994, 1995, 1996, 1997, 1998],
        '1999-2003': [1999, 2000, 2001, 2002, 2003],
        '2004-2008': [2004, 2005, 2006, 2007, 2008],
        '2009-2013': [2009, 2010, 2011, 2012, 2013],
        '2014-2019': [2014, 2015, 2016, 2017, 2018, 2019],
    }
    
    tasas_provinciales_por_periodos = {}
    for i, period in enumerate(periods):
        print(f"Recolectando datos para el período: {period}...")
        dataset_i = df\
            [df['año'].isin(periods[period])]\
            .drop(columns=['año', 'tasa'])\
            .groupby(['provincia_id'])\
            .sum()\
            .reset_index()

        dataset_i['tasa'] = \
            (dataset_i['fallecimientos'] / dataset_i['nacimientos']) *10_000

        dataset_i['periodo'] = period

        tasas_provinciales_por_periodos[period] = dataset_i

    print("OK.")

    f, ax = plt.subplots(
        nrows=1, ncols=5,
        figsize=(26, 8),
        constrained_layout=True
    )
    axs = ax.flatten()

    for i, period in enumerate(tasas_provinciales_por_periodos):
        # == Map: ==
        ax = axs[i]

        provincial_i = pandas.merge(
            shape,
            tasas_provinciales_por_periodos[period],
            on='provincia_id',
            how='left'
        )
        provincial_i.plot(
            ax=ax,
            column='tasa',
            cmap=cmap,
            edgecolor='none',
            linewidth=0.02,
            legend=True,
            legend_kwds={'shrink': 0.5},
        )

        for index,row in provincial_i.iterrows():
            xy=row['geometry'].centroid.coords[:]
            xytext=row['geometry'].centroid.coords[:]
            ax.annotate(
                f"{row['provincia_nombre']}\n{row['tasa']:0.2f}",
                xy=xy[0],
                xytext=xytext[0],
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=6,
                bbox=dict(boxstyle='square,pad=0.5', fc='#EEEEEE82', ec='none')
            )

        ax.axis('off')
        ax.set_title(f"Período {period}", fontsize=16)

    f.suptitle("Tasa por quinquenios", fontsize=20, y=1.08)

    plt.savefig(str(product), dpi=300)
    plt.close();
