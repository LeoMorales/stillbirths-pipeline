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
from pathlib import Path


# -

def __create_figure_provincial_rates(t, nacimientos, mortinatos, tasa,
        figure_title=f"Nacimientos, mortinatos y tasas"):
    f_height = 4
    f_width  = 8
    fig, ax1 = plt.subplots(figsize=(f_width, f_height), constrained_layout=True)

    ax1.set_xlabel('años')
    ax1.set_ylabel(
        'Nacimientos (azul)\n\nMortinatos (rojo)',
        rotation=0,
        ha='right'
    )
    ax1.plot(
        t,
        nacimientos,
        color='tab:blue'
    )

    ax1.plot(
        t,
        mortinatos,
        color='tab:red'
    )

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:orange'
    ax2.set_ylabel(
        'Tasa',
        color=color,
        rotation=0,
        ha='left'
    )  # we already handled the x-label with ax1
    ax2.plot(t, tasa, color=color, marker='.')
    ax2.tick_params(axis='y', labelcolor=color)

    #fig.tight_layout()  # otherwise the right y-label is slightly clipped
    ax1.set_title(figure_title)
    
    return fig, ax1, ax2


def __get_province_name_by_id():
    SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson'
    shape = geopandas.read_file(SHAPE_DIR)
    shape = shape[[
        'provincia_id', 'provincia_nombre',
        'departamento_id', 'departamento_nombre',
        'region_indec', 'geometry']]

    return {
        item['provincia_id']: item['provincia_nombre']
        for item
        in shape[['provincia_id', 'provincia_nombre']].to_dict(orient='records')
    }



# + tags=[]
def by_years(product, upstream):
    df = pandas.read_parquet(upstream['get_annual']['data'])

    provincias_id_nombre = __get_province_name_by_id()

    # setup:
    parent = Path(product)

    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)

    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)
    
    for province_id in provincias_id_nombre:
        # pick only one
        data_i = df[df.provincia_id == province_id]

        f, _, _ = __create_figure_provincial_rates(
            data_i['año'],
            data_i.nacimientos,
            data_i.fallecimientos,
            data_i.tasa,
            figure_title=f"Nacimientos, mortinatos y tasas para {provincias_id_nombre[province_id]}"
        )
        province_path_name = provincias_id_nombre[province_id].replace(' ', '_').strip().lower()
        output_file = f"{str(product)}/{province_path_name}.png"
        f.savefig(output_file, dpi=300)
        plt.close()


# + tags=[]
def by_quinquennio(product, upstream):
    df_quinquenios = pandas.read_parquet(upstream['get_quinquenial']['data'])
    provincias_id_nombre = __get_province_name_by_id()

    # setup:
    parent = Path(product)

    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)

    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)
    
    for province_id in provincias_id_nombre:
        # pick only one
        data_i = df_quinquenios\
            [df_quinquenios.provincia_id == province_id]

        f, _, _ = __create_figure_provincial_rates(
            data_i['periodo'],
            data_i.nacimientos,
            data_i.fallecimientos,
            data_i.tasa,
            figure_title=f"Nacimientos, mortinatos y tasas para {provincias_id_nombre[province_id]}"
        )
        province_path_name = provincias_id_nombre[province_id].replace(' ', '_').strip().lower()
        output_file = f"{str(product)}/{province_path_name}.png"
        f.savefig(output_file, dpi=300)
        plt.close()
# -


