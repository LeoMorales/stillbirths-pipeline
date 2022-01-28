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

def __plot_departments_grid(slice_data, contextual_data,
        col_wrap,
        time_col='año',
        rate_col='tasa',
        hue_col='departamento_nombre',
        figure_title='FIGURE',
        figure_name='figure.png'
    ):
    ''' Dibuja una grilla partiendo los datos de slice_data segun hue_col
    '''
    # Plot each deapartment's time series in its own facet
    g = seaborn.relplot(
        data=slice_data,
        x=time_col,
        y=rate_col,
        col=hue_col,
        hue=hue_col,
        kind="line",
        palette="crest",
        linewidth=4,
        zorder=5,
        col_wrap=col_wrap,
        height=2,
        aspect=1.5,
        legend=False
    )

    # fig size calculation:
    #
    plots_number = len(slice_data[hue_col].unique())
    row_n = plots_number // 3
    # if integer division is ligual to floating division, cells are sufficient, skip
    if ((plots_number / 3) - row_n) > 0:
        row_n += 1
    fig_size = 15, 2.5 * row_n

    g.fig.set_size_inches(*fig_size)

    # Iterate over each subplot to customize further
    for ax_title, ax in g.axes_dict.items():

        # Add the title as an annotation within the plot
        ax.text(
            .85, .85,
            ax_title,
            transform=ax.transAxes,
            horizontalalignment='right',
            fontweight="bold"
        )

        # Plot every year's time series in the background
        # plot the provincial context values!
        seaborn.lineplot(
            data=contextual_data,
            x=time_col,
            y=rate_col,
            units=time_col,
            estimator=None,
            color=".7",
            linewidth=1.5,
            ax=ax,
        )
        ax.tick_params(
            axis='x',
            rotation=45
        )

    # Reduce the frequency of the x axis ticks
    #ax.set_xticks(ax.get_xticks()[::2])

    # Tweak the supporting aspects of the plot
    g.set_titles("")
    g.set_axis_labels(
        time_col.capitalize(),
        rate_col.capitalize()
    )

    plt.suptitle(figure_title)
    plt.ioff()
    plt.savefig(
        figure_name, dpi=300, bbox_inches="tight")
    plt.close()


def __get_slices(provincial_data, col_work, rows=7, cols=3):
    ''' Devuelve grupos de datos (dfs) de rows*cols segun los valores unicos de la col_work
    
    Return:
    
        dict: {'02321': pandas.DataFrame, ...}
    '''
    # para el reporte, es conveniente tener figuras chicas (buenos aires por ej tiene muchos departamentos)
    # armamos un diccionario con los registros que van a dibujarse en una sola figura
    TOTAL = len(provincial_data[col_work].unique())
    BASE = 0

    STEP = rows * cols
    TOP = STEP

    part = 1
    slices = {}
    while BASE < TOTAL:
        slice_ids = provincial_data[col_work].unique()[BASE:TOP]
        slices[part] = provincial_data\
            [provincial_data.departamento_id.isin(slice_ids)]
        #print(figure_department_idx)
        BASE += STEP
        TOP += STEP
        part += 1
    
    return slices


# + tags=[]
def by_years(product, upstream):
    ''' Tarea que genera las figuras de lineplot con un gráfico
    con los valores de las tasas de cada departamento para cada una
    de las provincias
    '''
    ## initial setup (folder product):
    
    parent = Path(product)
    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)
    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)

    ## read data
    #df = pandas.read_parquet('../_products/rates/rates-by-year.parquet')
    df = pandas.read_parquet(upstream['get_annual']['data'])

    SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson'
    shape = geopandas.read_file(SHAPE_DIR)

    # obtenemos los nombres de provincia desde la capa
    province_names_dict = {
        item['provincia_id']: item['provincia_nombre']
        for item
        in shape[['provincia_id', 'provincia_nombre']].to_dict(orient='records')
    }
    # obtenemos los identificadores de provincia desde los datos
    provinces_ids = df.departamento_id.str.slice(0, 2).unique()

    COL_WRAP = 3
    TIME_COL='año'
    RATE_COL='tasa'
    HUE_COL='departamento_nombre'

    # bucle por cada provincia
    for province_id in provinces_ids:
        # provincia: filtrar sus datos
        provincial_data = \
            df[df.departamento_id.str.startswith(province_id)].copy()

        # obtener los nombres de cada departamento de la provincia
        # utilizamos los nombres de la capa.
        department_names_dict = {
            item['departamento_id']: item['departamento_nombre']
            for item
            in shape[shape.provincia_id == province_id][['departamento_id', 'departamento_nombre']].to_dict(orient='records')
        }

        # agregamos a los datos, una columna con el nombre de departamento
        provincial_data['departamento_nombre'] = \
            provincial_data.departamento_id.apply(lambda i: department_names_dict.get(i, '-'))
        # eliminamos aquellas filas que nos hayan quedado sin nombre de departamento
        provincial_data = provincial_data[provincial_data.departamento_nombre != '-']

        slices = __get_slices(provincial_data, 'departamento_id', cols=COL_WRAP)

        for slice_i in slices:
            # enviamos la figura a la carpeta final:
            province_name_in_path = province_names_dict[province_id].replace(' ', '_')
            output_file = f"{str(product)}/{province_name_in_path}_{slice_i}.png"
            
            __plot_departments_grid(
                slice_data= slices[slice_i],
                contextual_data=provincial_data,
                col_wrap=COL_WRAP,
                time_col=TIME_COL,
                rate_col=RATE_COL,
                hue_col=HUE_COL,
                figure_title=f"Provincia: {province_names_dict[province_id]} - ID: {province_id} - Parte {slice_i}",
                figure_name=output_file
            )


# + tags=[]
def by_quinquennios(product, upstream):
    ## initial setup (folder product):
    
    parent = Path(product)
    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)
    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)

    ## read data
    #df = pandas.read_parquet('../_products/rates/rates-by-quinquenios.parquet')
    df = pandas.read_parquet(upstream['get_quinquenial']['data'])

    SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson'
    shape = geopandas.read_file(SHAPE_DIR)

    # obtenemos los nombres de provincia desde la capa (lo necesitamos para el titulo de las figuras)
    province_names_dict = {
        item['provincia_id']: item['provincia_nombre']
        for item
        in shape[['provincia_id', 'provincia_nombre']].to_dict(orient='records')
    }
    # obtenemos los identificadores de provincia desde los datos para el loop
    provinces_ids = df.departamento_id.str.slice(0, 2).unique()

    COL_WRAP = 3
    TIME_COL='periodo'
    RATE_COL='tasa'
    HUE_COL='departamento_nombre'

    # bucle por cada provincia
    for province_id in provinces_ids:
        # provincia: filtrar sus datos
        provincial_data = \
            df[df.departamento_id.str.startswith(province_id)].copy()

        # obtener los nombres de cada departamento de la provincia
        # utilizamos los nombres de la capa. Los necesitamos para
        # partir los datos que van a ir a cada grafiquito dentro de la figura
        department_names_dict = {
            item['departamento_id']: item['departamento_nombre']
            for item
            in shape[shape.provincia_id == province_id][['departamento_id', 'departamento_nombre']].to_dict(orient='records')
        }

        # agregamos a los datos, una columna con el nombre de departamento
        provincial_data['departamento_nombre'] = \
            provincial_data.departamento_id.apply(lambda i: department_names_dict.get(i, '-'))
        # eliminamos aquellas filas que nos hayan quedado sin nombre de departamento
        provincial_data = provincial_data[provincial_data.departamento_nombre != '-']

        slices = __get_slices(provincial_data, 'departamento_id', cols=COL_WRAP)

        for slice_i in slices:
            # enviamos la figura a la carpeta final:
            province_name_in_path = province_names_dict[province_id].replace(' ', '_')
            output_file = f"{str(product)}/{province_name_in_path}_{slice_i}.png"

            __plot_departments_grid(
                slice_data= slices[slice_i],
                contextual_data=provincial_data,
                col_wrap=COL_WRAP,
                time_col=TIME_COL,
                rate_col=RATE_COL,
                hue_col=HUE_COL,
                figure_title=f"Provincia: {province_names_dict[province_id]} - ID: {province_id} - Parte {slice_i}",
                figure_name=output_file
            )
