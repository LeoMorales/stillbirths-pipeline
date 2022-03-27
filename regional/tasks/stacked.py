#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw
"""
import pandas
import matplotlib.pyplot as plt
from pathlib import Path
import shutil
from matplotlib import lines
from matplotlib import patches


def arrange(product, upstream):
    '''
    Convierte el dataframe:
        codigo_muerte   count   period      percentage
    0   P02             12680   1994-1998   31.785822
    1   P20             8692    1994-1998   21.788830
    2   P96             5044    1994-1998   12.644139
    [...]
    
    En el dataframe:
                    P00         P02         P20         P95         P96         Otros
    1994-1998   8.515492    31.785822   21.788830   8.959190    12.644139   16.306528
    1999-2003   8.150058    26.794170   19.593812   27.685994   2.078291    15.697674
    2004-2008   7.386145    22.957024   20.635022   30.519564   3.874278    14.627967
    [...]
    '''
    #df = pandas.read_parquet('../_products/percentages/percentages_country_quinquenal.parquet')
    df = pandas.read_parquet(upstream['get_quinquenal_national_level']['data'])

    # get the codes with the highest percentage
    codesHighestPercentage1994_1998 = \
        df[df.period == '1994-1998']\
            .sort_values(by='percentage', ascending=False)\
            .loc[:4]\
            .codigo_muerte.values
    
    # verbose too observe the order:
    periods = ['1994-1998', '1999-2003', '2004-2008', '2009-2013', '2014-2019']
    
    # filtrar los registros que pertenezcan a los periodos seleccionados y que sean de alguno de los códigos con mayor porcentaje:
    work_df = df[
        (df.period.isin(periods)) &
        (df.codigo_muerte.isin(codesHighestPercentage1994_1998))
    ]

    # sumamos los porcentajes del resto de los códigos para dibujar una barra que represente al resto:
    others_df = \
        df[
            (df.period.isin(periods)) &
            ~(df.codigo_muerte.isin(codesHighestPercentage1994_1998))
        ]\
        .groupby(['period'])\
        .sum()\
        .reset_index()


    others_df = others_df.set_index(others_df.period).drop(columns=['period', 'count'])
    others_df = others_df.rename(columns=dict(percentage='Otros'))
    others_df.index.name = None
    # result:
    #               Otros
    #    1994-1998  16.306528
    #    1999-2003  15.697674
    #    2004-2008  14.627967

    # ====
    # pivot:
    work_df_reshape = work_df.pivot(
        index='period',
        columns='codigo_muerte',
        values='percentage'
    )
    work_df_reshape.columns.name = None
    work_df_reshape.index.name = None

    # ====
    # add 'other' column:
    
    work_df = pandas.merge(work_df_reshape.reset_index(), others_df.reset_index())
    work_df.index = work_df['index']
    work_df.index.name = None
    work_df = work_df.drop(columns='index')

    work_df.to_parquet(str(product))


def draw(product, upstream):
    df = pandas.read_parquet(upstream['arrange'])
    
    names = df.index.values  # names = ('1994-1998','1999-2003',...)
    # colors = ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462']
    # colors = ['#d53e4f', '#fc8d59', '#fee08b', '#e6f598', '#99d594', '#3288bd']
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33']
    bottomBars = [0 for _ in range(len(df.index))]
    barWidth = 0.85
    
    fig, ax = plt.subplots(figsize=(12, 8))

    for i, col in enumerate(df.columns):
        currentBars = df[col].values

        # Create Bars
        plt.bar(
            names,
            currentBars,
            color=colors[i],
            edgecolor='white',
            width=barWidth,
            label=col,
            bottom=bottomBars
        )

        bottomBars = [i+j for i,j in zip(bottomBars, currentBars)]

    # Custom x axis
    plt.xticks(names, names)
    plt.xlabel("Período")
    
    ax.set_axisbelow(True)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_lw(1.5)

    # Add a legend
    plt.legend(loc='upper left', bbox_to_anchor=(1,1), ncol=1)

    # Make room on top and bottom
    # Note there's no room on the left and right sides
    fig.subplots_adjust(top=0.8, bottom=0.2)

    GREY = "#a2a2a2"
    DETAIL_COLOR = "#69b3a2"

    # Add title
    title = "Porcentajes por código de muerte"
    LEFT_START_POS = .01
    fig.text(
        LEFT_START_POS, 0.925, title,
        fontsize=22, fontweight="bold", fontfamily="Econ Sans Cnd"
    )

    # Add subtitle
    subtitle = "Argentina. Por quinquenios"
    fig.text(
        LEFT_START_POS, 0.875, subtitle, 
        fontsize=20, fontfamily="Econ Sans Cnd"
    )

    # Add caption
    caption="Fuente: Datos del Ministerio de Salud"
    fig.text(
        LEFT_START_POS, 0.12, caption, color=GREY, 
        fontsize=14, fontfamily="Econ Sans Cnd"
    )

    # Add authorship
    authorship="GIBEH IPCSH CENPAT-CONICET"
    fig.text(
        LEFT_START_POS, 0.08, authorship, color=GREY,
        fontsize=16, fontfamily="Milo TE W01"
    )

    # Add line and rectangle on top.
    fig.add_artist(lines.Line2D([0, 1], [1, 1], lw=3, color=DETAIL_COLOR, solid_capstyle="butt"))
    fig.add_artist(patches.Rectangle((0, 0.975), 0.05, 0.025, color=DETAIL_COLOR))
    # Show graphic
    plt.savefig(str(product), dpi=300)
