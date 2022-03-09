#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Plot departamental rates in lines
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

from stillbirths_package.utils import REGION_BY_PROVINCE_CODE, PROVINCE_NAME_BY_ID


# -

def __create_figure(data, lines_by_col, time_col, figure_title, output_file, xlabel):
    # reorder (pivot)
    plot_data = data.pivot(index=time_col, columns=lines_by_col)
    plot_data.index.name = None
    plot_data.columns = pandas.Index([c for _, c in plot_data.columns])

    # plot
    f, ax = plt.subplots(figsize=(12, 8))
    custom_params = {"axes.spines.right": False, "axes.spines.top": False}
    seaborn.set_theme(style="whitegrid", rc=custom_params)
    seaborn.lineplot(data=plot_data)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel('Tasa', fontsize=14)
    f.suptitle(
        figure_title,
        fontsize=16)
    
    # save
    f.savefig(output_file, dpi=300)
    plt.close()


# + tags=[]
def by_quinquennio(product, upstream):
    # setup:
    parent = Path(product)

    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)

    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)

    # read the data
    df = pandas.read_parquet(upstream['get_quinquenial']['data'])

    # get region names
    regions = list(set(REGION_BY_PROVINCE_CODE.values()))

    # create province name column
    df['provincia_nombre'] = df.provincia_id.replace(PROVINCE_NAME_BY_ID)

    lines_by_col = 'provincia_nombre'
    time_col = 'periodo'
    work_cols = [time_col, lines_by_col, 'tasa']
    
    for region_i in regions:
        
        province_codes = [
            code
            for code, region
            in REGION_BY_PROVINCE_CODE.items()
            if region == region_i
        ]
        
        data = df[df.provincia_id.isin(province_codes)][work_cols]
        provinces_in_region_path_name = region_i.lower()
        output_file = f"{str(product)}/{provinces_in_region_path_name}.png"
        
        __create_figure(
            data, lines_by_col, time_col,
            figure_title=f"Tasas de mortinatos\nProvincias de la región {region_i}\nPeríodo: 1994-2019",
            output_file=output_file,
            xlabel='Quinquenio'
        )


# + tags=[]
def by_years(product, upstream):

    # setup:
    parent = Path(product)

    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)

    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)
    
    # read the data
    df = pandas.read_parquet(upstream['get_annual']['data'])

    # get region names
    regions = list(set(REGION_BY_PROVINCE_CODE.values()))

    # create province name column
    df['provincia_nombre'] = df.provincia_id.replace(PROVINCE_NAME_BY_ID)

    lines_by_col = 'provincia_nombre'
    time_col = 'año'
    work_cols = [time_col, lines_by_col, 'tasa']
    
    # for each region
    for region_i in regions:
        
        province_codes = [
            code
            for code, region
            in REGION_BY_PROVINCE_CODE.items()
            if region == region_i
        ]
        
        data = df[df.provincia_id.isin(province_codes)][work_cols]
        provinces_in_region_path_name = region_i.lower()
        output_file = f"{str(product)}/{provinces_in_region_path_name}.png"
        
        __create_figure(
            data, lines_by_col, time_col,
            figure_title=f"Tasas de mortinatos\nProvincias de la región {region_i}\nPeríodo: 1994-2019",
            output_file=output_file,
            xlabel='Año'
        )
