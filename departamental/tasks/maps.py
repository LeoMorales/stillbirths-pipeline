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
    #df = pandas.read_parquet('../_products/rates/rates-by-year.parquet')

    SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson'
    shape = geopandas.read_file(SHAPE_DIR)
    shape = shape[[
        'departamento_id', 'departamento_nombre', 'provincia_nombre', 'geometry']]

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
            on='departamento_id'
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
        "Tasas departamentales por año",
        fontsize=20
    )
    filled_n = ((nrows*ncols)-(i+1))  # la cantidad de celditas, menos hasta donde se llegó
    for ax_to_delete in axs[filled_n*-1:]:
        plt.delaxes(ax_to_delete)


    plt.savefig(str(product), dpi=300)
    plt.close();


# + tags=[]
def by_quinquenios(product, upstream):
    '''Dibuja los paras de tasas por quinquenios
    '''
    df = pandas.read_parquet(upstream['get_quinquenial']['data'])
    #df = pandas.read_parquet('../_products/rates/rates-by-quinquenios.parquet')

    SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson'
    shape = geopandas.read_file(SHAPE_DIR)
    shape = shape[[
        'departamento_id', 'geometry']]

    cmap = seaborn.diverging_palette(250, 5, as_cmap=True)

    f, ax = plt.subplots(
        nrows=1, ncols=5,
        figsize=(26, 8),
        constrained_layout=True
    )
    axs = ax.flatten()

    for i, (period, df_period) in enumerate(df.groupby('periodo')):
        # == Map: ==
        ax = axs[i]

        # black map background:
        shape.plot(
            ax=ax,
            color='black'
        )    

        # main map
        pandas.merge(
            shape,
            df_period,
            on='departamento_id',
            how='left'
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
        ax.set_title(f"Período {period}", fontsize=16)

    f.suptitle("Tasa por quinquenios", fontsize=20, y=1.08)
    plt.savefig(str(product), dpi=300)
    plt.close();
