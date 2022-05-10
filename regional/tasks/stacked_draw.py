#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stacked bar charts are drawn here
"""
import pandas
from pathlib import Path
import shutil
from stillbirths_package import plot_utils


# + active=""
# def __draw_stacked(output_destination, arranged_df,
#         title="Porcentajes por código de muerte",
#         subtitle="Argentina. Por quinquenios"
#     ):
#     
#     names = arranged_df.index.values  # names = ('1994-1998','1999-2003',...)
#     bottomBars = [0 for _ in range(len(arranged_df.index))]
#     barWidth = 0.85
#     
#     fig, ax = plt.subplots(figsize=(12, 8))
#
#     for i, col in enumerate(sorted(arranged_df.columns)):
#         currentBars = arranged_df[col].values
#
#         # Create Bars
#         plt.bar(
#             names,
#             currentBars,
#             color=CODES_AND_COLORS.get(col, 'grey'),
#             edgecolor='lightgrey',
#             width=barWidth,
#             label=col,
#             bottom=bottomBars
#         )
#
#         bottomBars = [i+j for i,j in zip(bottomBars, currentBars)]
#
#     # Custom x axis
#     plt.xticks(names, names)
#     plt.xlabel("Período")
#     
#     ax.set_axisbelow(True)
#     ax.spines["right"].set_visible(False)
#     ax.spines["top"].set_visible(False)
#     ax.spines["bottom"].set_visible(False)
#     ax.spines["left"].set_lw(1.5)
#
#     # Add a legend
#     plt.legend(loc='upper left', bbox_to_anchor=(1,1), ncol=1)
#
#     # Make room on top and bottom
#     # Note there's no room on the left and right sides
#     fig.subplots_adjust(top=0.8, bottom=0.2)
#
#     GREY = "#a2a2a2"
#     DETAIL_COLOR = "#69b3a2"
#
#     # Add title
#     LEFT_START_POS = .01
#     fig.text(
#         LEFT_START_POS, 0.925, title,
#         fontsize=22, fontweight="bold", fontfamily="Econ Sans Cnd"
#     )
#
#     # Add subtitle
#     fig.text(
#         LEFT_START_POS, 0.875, subtitle, 
#         fontsize=20, fontfamily="Econ Sans Cnd"
#     )
#
#     # Add caption
#     caption="Fuente: Datos del Ministerio de Salud"
#     fig.text(
#         LEFT_START_POS, 0.12, caption, color=GREY, 
#         fontsize=14, fontfamily="Econ Sans Cnd"
#     )
#
#     # Add authorship
#     authorship="GIBEH IPCSH CENPAT-CONICET"
#     fig.text(
#         LEFT_START_POS, 0.08, authorship, color=GREY,
#         fontsize=16, fontfamily="Milo TE W01"
#     )
#
#     # Add line and rectangle on top.
#     fig.add_artist(lines.Line2D([0, 1], [1, 1], lw=3, color=DETAIL_COLOR, solid_capstyle="butt"))
#     fig.add_artist(patches.Rectangle((0, 0.975), 0.05, 0.025, color=DETAIL_COLOR))
#     # Show graphic
#     plt.savefig(output_destination, dpi=300)
# -

def regional_quinquenal(product, upstream):
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
        upstream['get_regional_arranged_at_quinquenal'])
    
    # ==========
    # loop:
    for region_i, df_region_i in df_region.groupby(['region']):
        
        # obtener los códigos para los cuales se van a crear barras
        # (el grupo de top 5 de códigos puede cambiar de region en región)
        
        # quitar la columna región, tomar el primer renglón, ordenar los porcentages,
        # quedarse con los 5 primeros códigos + la col "Otros"
        code_cols = df_region_i\
            .drop(columns='region')\
            .iloc[0]\
            .sort_values(ascending=False)\
            .index[:6].values
        
        plot_utils.draw_stacked(
            f"{str(product)}/{region_i}-quinquenal.png",
            df_region_i[code_cols],
            subtitle=f"Región: {region_i.capitalize()}. Por quinquenios"

        )
