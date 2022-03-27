#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw
"""
import pandas
import glob
import matplotlib.pyplot as plt
import seaborn
from matplotlib import lines
from matplotlib import patches
from matplotlib.patheffects import withStroke
from pathlib import Path
import shutil

# +
from PIL import Image
import numpy as np

def __create_collage():
    '''TODO: Terminar...'''
    # open images by providing path of images
    img1 = Image.open("../_products/percentages/regional/Cuyo-1994-1998.png")
    img2 = Image.open("../_products/percentages/regional/Cuyo-1999-2003.png")
    img3 = Image.open("../_products/percentages/regional/Cuyo-2004-2008.png")
    img4 = Image.open("../_products/percentages/regional/Cuyo-2009-2013.png")

    img1 = img1.resize((1920, 1280))
    img2 = img2.resize((1920, 1280))
    img3 = img3.resize((1920, 1280))
    img4 = img4.resize((1920, 1280))

    #create arrays of above images
    img1_array = np.array(img1)
    img2_array = np.array(img2)
    img3_array = np.array(img3)
    img4_array = np.array(img4)


    # ====== collage of 2 images ====== 
    # arrange arrays of two images in a single row 
    imgg = np.hstack([img1_array , img2_array]) 
    #create image of imgg array
    finalimg = Image.fromarray(imgg)
    #provide the path with name for finalimg where you want to save it
    finalimg.save("collagemaker.png")
    print("First image saved")


    # ====== collage of 4 images ====== 
    # arrange arrays of four images in two rows
    imgg1 = np.vstack([np.hstack([img1_array , img2_array]) , np.hstack([img3_array , img4_array])]) 
    #create image of imgg1 array
    finalimg1 = Image.fromarray(imgg1)
    #provide the path with name for finalimg1 where you want to save it
    finalimg1.save("collagemaker1.png")
    print("Second image saved")


# -

def __create_figure(names, counts, output_destination,
        title="Porcentajes por código de muerte",
        subtitle="Argentina, período 1994-1998",
        caption="Fuente: Datos del Ministerio de Salud",
        authorship="GIBEH IPCSH CENPAT-CONICET",
        draw_label_on_the_bar_until=4
    ):
    # The positions for the bars
    # This allows us to determine exactly where each bar is located
    y = [i * 0.9 for i in range(len(names))]

    # The colors
    BAR_COLOR = "#076fa2"
    DETAIL_COLOR = "#69b3a2"
    BLACK = "#202020"
    GREY = "#a2a2a2"

    fig, ax = plt.subplots(figsize=(12, len(names)*.5))

    ax.barh(y, counts, height=0.55, align="edge", color=BAR_COLOR);

    ax.xaxis.set_ticks([i * 5 for i in range(0, 12)])
    ax.xaxis.set_ticklabels([i * 5 for i in range(0, 12)], size=16, fontfamily="Econ Sans Cnd", fontweight=100)
    ax.xaxis.set_tick_params(labelbottom=False, labeltop=True, length=0)

    x_max = counts.max() + 5
    ax.set_xlim((0, x_max))
    ax.set_ylim((0, len(names) * 0.9 - 0.2))

    # Set whether axis ticks and gridlines are above or below most artists.
    ax.set_axisbelow(True)
    ax.grid(axis = "x", color="#A8BAC4", lw=1.2)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_lw(1.5)
    # This capstyle determines the lines don't go beyond the limit we specified
    # see: https://matplotlib.org/stable/api/_enums_api.html?highlight=capstyle#matplotlib._enums.CapStyle
    ax.spines["left"].set_capstyle("butt")

    # Hide y labels
    ax.yaxis.set_visible(False)

    PAD = 0.3
    LABEL_IN_BAR_LIMIT = draw_label_on_the_bar_until
    for i, (name, count, y_pos) in enumerate(zip(names, counts, y)):
        x = 0
        color = "white"
        path_effects = None
        if count < LABEL_IN_BAR_LIMIT:
            x = count
            color = BAR_COLOR    
            path_effects=[withStroke(linewidth=6, foreground="white")]
        
        bar_label = name
        if i == 0:
            # (porque dibuja de abajo hacia arriba)
            bar_label = f"{name} ({count:0.2f} %)"

        ax.text(
            x + PAD, y_pos + 0.5 / 2, bar_label, 
            color=color, fontfamily="Econ Sans Cnd", fontsize=18, va="center",
            path_effects=path_effects
        ) 

    # Make room on top and bottom
    # Note there's no room on the left and right sides
    fig.subplots_adjust(left=0.005, right=1, top=0.8, bottom=0.1)


    # Add title
    fig.text(
        0, 0.925, title, 
        fontsize=22, fontweight="bold", fontfamily="Econ Sans Cnd"
    )
    # Add subtitle
    fig.text(
        0, 0.875, subtitle, 
        fontsize=20, fontfamily="Econ Sans Cnd"
    )

    # Add caption
    fig.text(
        0, 0.06, caption, color=GREY, 
        fontsize=14, fontfamily="Econ Sans Cnd"
    )

    # Add authorship
    fig.text(
        0, 0.005, authorship, color=GREY,
        fontsize=16, fontfamily="Milo TE W01"
    )

    # Add line and rectangle on top.
    fig.add_artist(lines.Line2D([0, 1], [1, 1], lw=3, color=DETAIL_COLOR, solid_capstyle="butt"))
    fig.add_artist(patches.Rectangle((0, 0.975), 0.05, 0.025, color=DETAIL_COLOR))

    # Set facecolor, useful when saving as .png
    fig.set_facecolor("white")

    fig.savefig(output_destination, dpi=300)


def draw_quinquenal_national_level(product, upstream):
    ''' Crea una figura para cada período.'''
    
    # ==========
    # setup:
    parent = Path(product)

    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)

    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)
    
    # ==========
    # data:
    df_country = pandas.read_parquet(
        upstream['get_quinquenal_national_level']['data'])
    
    # ==========
    # loop:
    for period_i, data_i in df_country.groupby('period'):
        
        # period_i like '1994-1998'
        LIMIT = 0.1
        plot_data = data_i[data_i.percentage > LIMIT]

        # una sola barra para los otros códigos
        percentage_less_than_limit = data_i[~(data_i.percentage > LIMIT)]
        other_codes_sum = percentage_less_than_limit.percentage.sum()
        number_of_diff_codes = len(percentage_less_than_limit.codigo_muerte.unique())

        # agregamos el nuevo renglon
        plot_data = plot_data.append(
            pandas.DataFrame(dict(
                codigo_muerte=[f'Otros ({number_of_diff_codes})'],
                count=[-1],
                percentage=[other_codes_sum]
            )))

        plot_data = \
            plot_data\
                .sort_values(by='percentage', ascending=True)\
                .reset_index(drop=True)

        counts = plot_data.percentage
        names = plot_data.codigo_muerte

        __create_figure(
            names, counts,
            f"{str(product)}/{period_i}.png",
            subtitle=f"Argentina. Período {period_i}. Porcentajes mayores a {LIMIT}%"
        )


def draw_quinquenal_regional_level(product, upstream):
    ''' Crea una figura para cada período y region'''
    # ==========
    # setup:
    parent = Path(product)

    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)

    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)
    
    # ==========
    # data:
    df_region = pandas.read_parquet(
        upstream['get_quinquenal_regional_level']['data'])
    
    LIMIT = 0.1
    # ==========
    # loop:
    for (region_i, period_i), data_i in df_region.groupby(['region', 'period']):
        
        # period_i like '1994-1998'
        plot_data = data_i[data_i.percentage > LIMIT]

        # una sola barra para los otros códigos
        percentage_less_than_limit = data_i[~(data_i.percentage > LIMIT)]
        other_codes_sum = percentage_less_than_limit.percentage.sum()
        number_of_diff_codes = len(percentage_less_than_limit.codigo_muerte.unique())

        # agregamos el nuevo renglon
        plot_data = plot_data.append(
            pandas.DataFrame(dict(
                codigo_muerte=[f'Otros ({number_of_diff_codes})'],
                count=[-1],
                percentage=[other_codes_sum]
            )))

        plot_data = \
            plot_data\
                .sort_values(by='percentage', ascending=True)\
                .reset_index(drop=True)

        counts = plot_data.percentage
        names = plot_data.codigo_muerte

        __create_figure(
            names, counts,
            f"{str(product)}/{region_i}-{period_i}.png",
            subtitle=f"Region {region_i.capitalize()}. Período {period_i}. Porcentajes mayores a {LIMIT}%",
            draw_label_on_the_bar_until=2.5
        )
