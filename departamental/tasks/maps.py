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
from matplotlib.patches import Patch
from matplotlib import colors
from matplotlib.legend_handler import HandlerBase
from matplotlib.patches import Rectangle

from stillbirths_package import plot_utils
from stillbirths_package.utils import GROUP_CODES


# + tags=[]
def by_years(product, upstream):
    ''' Dibuja una grilla con un mapa departamental de la Argentina por cada año.
    '''
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
    ''' Dibuja una grilla con un mapa departamental de la Argentina por cada quinquenio.
    '''
    df = pandas.read_parquet(upstream['rates__get_quinquenial']['data'])
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


# -

class HandlerColormap(HandlerBase):
    def __init__(self, cmap, num_stripes=8, **kw):
        HandlerBase.__init__(self, **kw)
        self.cmap = cmap
        self.num_stripes = num_stripes
    def create_artists(self, legend, orig_handle, 
                       xdescent, ydescent, width, height, fontsize, trans):
        stripes = []
        for i in range(self.num_stripes):
            s = Rectangle([xdescent + i * width / self.num_stripes, ydescent], 
                          width / self.num_stripes, 
                          height, 
                          fc=self.cmap((2 * i + 1) / (2 * self.num_stripes)), 
                          transform=trans)
            stripes.append(s)
        return stripes


# + tags=[]
def get_code_percentages_quinquenios(product, upstream):
    '''
    '''    
    ## initial setup (folder product):
    parent = Path(product)
    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)
    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)

    # [ ] - leer los datos
    df = pandas.read_parquet(
        upstream['aggr__get_percentages_for_each_code_group'])

    # [ ] - leer la capa
    SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson'
    shape = geopandas.read_file(SHAPE_DIR)
    shape = shape[['departamento_id', 'geometry']]

    # [ ] - crear el mapa de colores
    cmap = seaborn.diverging_palette(250, 5, as_cmap=True)

    # [ ] - obtener una referencia con los códigos de defunciones ya agrupados (por una tarea aggr)
    for codeGroup, codeGroup_df in df.groupby(['code_group']):

        # [ ] - Obtener la cantidad de quinquenios que tiene el sub-dataset:
        numberOfPeriods = len(codeGroup_df.period.unique())
        # One figure for each group of codes:
        fig, ax = plt.subplots(
            nrows=1, ncols=numberOfPeriods,
            figsize=(18, 8), #constrained_layout=True
        )
        axs = ax.flatten()

        pmarks = []

        for i, (period, df_slice) in enumerate(codeGroup_df.groupby(['period'])):

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
                df_slice,
                on='departamento_id',
                how='left'
            ).plot(
                ax=ax,
                column='porcentaje_en_departmento',
                cmap=cmap,
                edgecolor='none',
                linewidth=0.02,
                legend=True,
                legend_kwds={'shrink': 0.5},
                vmax=100
            )

            ax.axis('off')
            ax.set_title(f"Period {period}", fontsize=16)

        # [ ] - Agregar anotaciones:
        fig = plot_utils.annotate_figure(
            fig,
            title=f"Choropleth map",
            subtitle=f"Quinquennial Analysis: '{codeGroup}' from 1994 to 2019",
            caption=f"\n\nSource: Ministerio de Salud de la República Argentina",
            authorship="GIBEH IPCSH CENPAT-CONICET"
        )
        fig.patch.set_facecolor('white')
        fig.patch.set_alpha(0.8)
        fig.set_constrained_layout(True)
        
        # Add a genaral legend:
        cmaps = [cmap, colors.ListedColormap(['black', 'black'])]
        cmap_labels = [
            f"Percentage of '{codeGroup[:14]}{'...' if len(codeGroup) > 14 else '' }' over the total number of stillbirths",
            "No data"]
        # create proxy artists as handles:
        cmap_handles = [Rectangle((0, 0), 1, 1) for _ in cmaps]
        handler_map = dict(zip(cmap_handles, 
                               [HandlerColormap(cm, num_stripes=8) for cm in cmaps]))
        plt.legend(handles=cmap_handles, 
                   labels=cmap_labels, 
                   handler_map=handler_map, 
                   fontsize=12,
                   loc='upper center', bbox_to_anchor=(0.2, -0.05)
        )
        
        # Save and close plt
        plt.savefig(f"{str(product)}/choropleth-{codeGroup}.png", dpi=300)
        plt.close();
