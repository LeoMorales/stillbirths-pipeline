#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Get departamental cluster
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
from stillbirths_package.utils import GROUP_CODES
# -

from stillbirths_package import spatial


# + tags=[]
def get_quinquennial_labels(product, upstream):
    ''' Guarda los valores del Moran para el atributo `tasa` departamental por periodo.
    
    Returns:
    
        - moran_results:
                moran_i  p_sim    periodo
            0   0.301526  0.001  1994-1998
            1   0.472844  0.001  1999-2003
            2   0.438105  0.001  2004-2008
        
        - cluster_labels:
                departamento_id    periodo      cluster
            0   06280              1994-1998    not-significant
            1   06357              1994-1998    not-significant
            2   06518              1994-1998    not-significant
    '''
    df = pandas.read_parquet(upstream['rates__get_quinquenial']['data'])
    #df = pandas.read_parquet('../_products/rates/rates-by-quinquenios.parquet')

    SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson'
    shape = geopandas.read_file(SHAPE_DIR)
    shape = shape[[
        'departamento_id', 'departamento_nombre', 'provincia_nombre', 'geometry']]

    clusterDataframes = []
    moranDataframes = []
    
    for period_i in df['periodo'].unique():

        df_i = pandas.merge(
            shape,
            df[df['periodo'] == period_i],
            on='departamento_id'
        )

        w, moran, lisa = spatial.get_spatials(
            shape=df_i,
            attribute='tasa',
        )

        # [ ] - Contar las cantidades por cada cluster
        quadfilter = (lisa.p_sim <= (.05)) * (lisa.q)
        spotLabels = ['not-significant', 'hot-spot', 'donut', 'cold-spot', 'diamond']
        labels = [spotLabels[i] for i in quadfilter]

        # [ ] - Asignar una nueva variable, proyectar las dos columnas de interés y guardar.
        clusterDataframes.append(
            df_i
                .assign(cluster=labels)
                [['departamento_id', 'periodo', 'cluster']]
                .copy()
        )
        # [ ] - Guardar también el indicador de Moran calculado y su p-value
        moranDataframes.append(
            pandas.DataFrame(
                {
                    'moran_i': [moran.I],
                    'p_sim': [moran.p_sim],
                    'periodo': [period_i]
                }
            ))

    labels_df = pandas.concat(clusterDataframes).reset_index(drop=True)
    labels_df.to_parquet(str(product['cluster_labels']))

    moran_df = pandas.concat(moranDataframes).reset_index(drop=True)
    moran_df.to_parquet(str(product['moran_results']))


# + tags=[]
def get_lisa_labels_for_each_decease_code(product, upstream):
    ''' 
    '''
    df = pandas.read_parquet(upstream['raw__get_percentage_for_each_cause'])
    df = df.rename(columns=dict(period='periodo', department_id='departamento_id'))
    #df = pandas.read_parquet('../_products/rates/rates-by-quinquenios.parquet')

    SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson'
    shape = geopandas.read_file(SHAPE_DIR)
    shape = shape[[
        'departamento_id', 'departamento_nombre', 'provincia_nombre', 'geometry']]

    clusterDataframes = []
    moranDataframes = []

    # for each period
    for period_i, df_period_i in df.groupby(['periodo']):

        # and then, for each group of codes:
        for groupCode in GROUP_CODES:
            
            try:

                # [ ] - filter by group 
                df_i = df_period_i[(df_period_i.codigo_muerte.isin(GROUP_CODES[groupCode]))]

                if len(df_i) < 10:
                    continue  # con el siguieente grupo

                # [ ] - accumulate percentages
                df_i = df_i\
                    .groupby('departamento_id')\
                    .sum()\
                    .reset_index()

                df_i = pandas.merge(shape, df_i,
                                    on='departamento_id')

                # Calculo de los estadísticos de Moran:
                w, moran, lisa = spatial.get_spatials(
                    shape=df_i,
                    attribute='porcentaje_en_departmento',
                    #strategy='distance_band',
                    #band_distance=1000,            
                )

                # [ ] - Asignar una etiqueta de cluster a cada departamento
                quadfilter = (lisa.p_sim <= (.05)) * (lisa.q)
                spotLabels = ['not-significant', 'hot-spot', 'donut', 'cold-spot', 'diamond']
                labels = [spotLabels[i] for i in quadfilter]

                # [ ] - Guardar el dataset en la lista.
                ordered_columns = ['departamento_id', 'codes', 'cluster', 'period', 'porcentaje_en_departmento']
                clusterDataframes.append(
                    df_i
                        .assign(cluster=labels, codes=groupCode, period=period_i)
                        [ordered_columns]
                        .copy()
                )
                # [ ] - Guardar también el indicador de Moran calculado y su p-value
                moranDataframes.append(
                    pandas.DataFrame(
                        {
                            'codes': [groupCode],
                            'periodo': [period_i],
                            'moran_i': [moran.I],
                            'p_sim': [moran.p_sim]
                        }
                    ))
        
            except IndexError:
                print(f"Error con los códigos: {groupCode}\nPeriodo: {period_i}\nTamaño de los datos: {len(df_i)}")
                continue

    labels_df = pandas.concat(clusterDataframes).reset_index(drop=True)
    labels_df.to_parquet(str(product['cluster_labels']))

    moran_df = pandas.concat(moranDataframes).reset_index(drop=True)
    moran_df.to_parquet(str(product['moran_results']))


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
