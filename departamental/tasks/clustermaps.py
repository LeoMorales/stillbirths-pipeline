#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Plot departamental cluster maps
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
from collections import Counter
from matplotlib.patches import Patch
from matplotlib import lines
from matplotlib import patches
from pathlib import Path
from stillbirths_package import plot_utils


def __get_palettes(labels):
    #label_colors = ['lightgrey', 'red', 'cornflowerblue', 'blue', 'orange']
    spot_labels = ['Not significant', 'Hot spot', 'Donut', 'Cold spot', 'Diamond']
    edge_colors = ['white', '#FFE6E6', '#96b6f0', '#050568', '#F76E11']
    edge_palette = {
        label: color
        for label, color
        in zip(spot_labels, edge_colors)
    }

    labels_counter = Counter(labels)

    # [ ] - Crear un arreglo de colores
    NS_COLOR = '#bababa'
    HOT_COLOR = '#d7191c'
    DONUT_COLOR = '#abd9e9'
    COLD_COLOR = '#2c7bb6'
    DIAMOND_COLOR = '#fdae61'

    # [ ] - Arreglo que posicionalmente se corresponde si tuvieramos todas las categorias:
    cluster_colors = [
        NS_COLOR,
        HOT_COLOR,
        DONUT_COLOR,
        COLD_COLOR,
        DIAMOND_COLOR,    
    ]

    # [ ] - Remover aquellos colores que no se utilicen
    spot_labels_in_dataset = spot_labels[:]
    if labels_counter.get('Donut', 0) == 0:
        cluster_colors.pop(cluster_colors.index(DONUT_COLOR))
        spot_labels_in_dataset.pop(spot_labels_in_dataset.index('Donut'))
    if labels_counter.get('Diamond', 0) == 0:
        cluster_colors.pop(cluster_colors.index(DIAMOND_COLOR))
        spot_labels_in_dataset.pop(spot_labels_in_dataset.index('Diamond'))


    tracts_palette = {
        label: color
        for label, color
        in zip(spot_labels_in_dataset, cluster_colors)
    }
    
    return tracts_palette, edge_palette


def __plot_map(data_shape, background_shape, groupby_col, tracts_palette, edge_palette, output_file,
        figure_title='Hotspots / Coldspots / Outliers',
        ax=None
    ):
    '''
    Dibuja el mapa de clusters.
    
    Args:
    
        data_shape (geopandas.GeoDataFrame): La capa que tiene las etiquetas.
        
        background_shape (geopandas.GeoDataFrame): La capa de fondo.
        
        groupby_col (str): Columna por la cual se pinta el mapa.
        
        tracts_palette (dict): Etiqueta de cluster -> color del polígono.
        
        edge_palette (dict): Etiqueta de cluster -> color del borde del polígono.
        
        output_file (str): Ruta destino de la figura creada.
        
        figure_title (str): Valor por defecto `Hotspots / Coldspots / Outliers`.
    '''
    
    useCustomAxes = not ax is None
    if not useCustomAxes:
        f, ax = plt.subplots(
            figsize=(12, 12),
            constrained_layout=True
        )
    
    # background map:
    background_shape.plot(color='black', ax=ax)

    pmarks = []
    for ctype, data in data_shape.groupby(groupby_col):
        # Define the color for each group using the dictionary
        color = tracts_palette[ctype]
        edge_color = edge_palette[ctype]

        # Plot each group using the color defined above
        data.plot(
            color=color,
            ax=ax,
            label=ctype,
            edgecolor=edge_color
        )

        pmarks.append(
            Patch(
                facecolor=color,
                label="{} ({})".format(ctype, len(data))
            )
        )

    # legend:
    # -> add a 'no-data' tag 
    noDataQty = len(background_shape) - len(data_shape)
    pmarks.append(
        Patch(
            facecolor='black',
            label=f"No data ({noDataQty})"
        )
    )
    legend_title = f'LISA Cluster Map [{len(data_shape)}]'
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(
        title=legend_title,
        handles=[*handles,*pmarks],
        loc='upper right',
        prop={'size': 12}
    )

    ax.set(title=figure_title)
    ax.set_axis_off()
    y_pos = -0.1
    x_pos = .8
    bbox_to_anchor = (x_pos, y_pos, 0.5, .5)

    ax.get_legend().set_bbox_to_anchor(bbox_to_anchor)
    plt.tight_layout()
    
    if not useCustomAxes:
        f.tight_layout()
        f.savefig(output_file)
        plt.close()
    return


def get_quinquennial(product, upstream):
    '''
    Retorna una figura con un mapa argentino departamental por cada quinquenio en el cual se identifican
    los hot spots, cold spots y los outliers espaciales para el atributo tasa de mortinatos.
    '''
    # [ ] Leer los datos
    #df_moran_labels = pandas.read_parquet('../_products/spatial_processing/cluster-labels-by-quinquenios.parquet')
    df_moran_labels = pandas.read_parquet(upstream['spatial_processing__get_quinquennial_labels']['cluster_labels'])
    #df_moran = pandas.read_parquet('../_products/spatial_processing/moran-indexes-by-quinquenios.parquet')
    df_moran = pandas.read_parquet(upstream['spatial_processing__get_quinquennial_labels']['moran_results'])

    #shape = geopandas.read_file(departments_shape_file)
    shape = geopandas.read_file('/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson')
    shape = shape.drop(columns=["provincia_id", "region_name", "region_indec"])


    # [ ] Re-escribir las etiquetas para la presentación
    data_labels = ['not-significant', 'hot-spot', 'donut', 'cold-spot', 'diamond']
    spot_labels = ['Not significant', 'Hot spot', 'Donut', 'Cold spot', 'Diamond']
    rename_labels = {
        original_label: new_label
        for original_label, new_label
        in zip(data_labels, spot_labels)
    }

    fig, ax = plt.subplots(
        nrows=1, ncols=5,
        figsize=(28, 12),
        constrained_layout=True
    )
    axs = ax.flatten()

    for i, (period, df_period) in enumerate(df_moran_labels.groupby('periodo')):
        # == Map: ==
        ax = axs[i]

        gdf_moran_labels = pandas.merge(
            shape,
            df_period,
            on='departamento_id',
            how='right'
        )

        # [ ] Armar el título
        # moran_I = 0.26  # df_moran_labels_moran.loc['moran_i', 'value']
        moran_I = df_moran[df_moran['periodo'] == period].reset_index().loc[0]['moran_i']
        #moran_p_sim = 0.001 # df_moran_labels_moran.loc['p_sim', 'value']
        moran_p_sim = df_moran[df_moran['periodo'] == period].reset_index().loc[0]['p_sim']
        moran_annotation = f'''
            Moran I: {moran_I:0.2f}
            p-value:{moran_p_sim}
        '''
        ax.text(-57, -55, moran_annotation,
                size=12,
                color='#0a0a0f',
                style='italic')

        # [ ] Re-escribir las etiquetas:
        gdf_moran_labels['label'] = gdf_moran_labels.cluster.replace(rename_labels)

        # [ ] - Armar las paletas
        tracts_palette, edge_palette = __get_palettes(gdf_moran_labels.label)

        # [] - Dibujar
        __plot_map(
            data_shape=gdf_moran_labels,
            background_shape=shape,
            groupby_col='label',
            tracts_palette=tracts_palette,
            edge_palette=edge_palette,
            output_file='-',
            figure_title=f'Period: {period}',
            ax=ax
        )


    # [ ] - Agregar anotaciones:

    fig = plot_utils.annotate_figure(
        fig,
        title='Moran Statistics: Stillbirth Rates',
        subtitle='Quinquennial Analysis from 1994 to 2019',
        caption="Source: Ministerio de Salud de la República Argentina",
        authorship="GIBEH IPCSH CENPAT-CONICET"
    )

    fig.patch.set_facecolor('white')
    fig.patch.set_alpha(0.8)

    plt.savefig(str(product), dpi=300)
    plt.close();


def get_quinquennial_for_codes(product, upstream):
    ''' Crea una figura por cada grupo de códigos de fallecimiento.
    Cada figura tiene cinco mapas, uno por cada quinquenio desde 1994.
    '''
    ## initial setup (folder product):
    parent = Path(product)
    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)
    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)

    # [ ] Leer los datos
    #df_moran_labels = pandas.read_parquet('../_products/spatial_processing/codigos-etiquetas-cluster-por-quinquenios.parquet')
    df_moran_labels = pandas.read_parquet(
        upstream['spatial_processing__get_lisa_labels_for_each_decease_code']['cluster_labels'])
    #df_moran = pandas.read_parquet('../_products/spatial_processing/codigos-moran-por-quinquenios.parquet')
    df_moran = pandas.read_parquet(
        upstream['spatial_processing__get_lisa_labels_for_each_decease_code']['moran_results'])

    #shape = geopandas.read_file(departments_shape_file)
    shape = geopandas.read_file('/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson')

    shape = shape[["departamento_id", "geometry"]]

    groupsOfLabels = df_moran_labels.codes.unique()

    # [ ] Re-escribir las etiquetas para la presentación
    data_labels = ['not-significant', 'hot-spot', 'donut', 'cold-spot', 'diamond']
    spot_labels = ['Not significant', 'Hot spot', 'Donut', 'Cold spot', 'Diamond']
    rename_labels = {
        original_label: new_label
        for original_label, new_label
        in zip(data_labels, spot_labels)
    }


    for codeGroup_i in groupsOfLabels:
        ## One figure for each group of deceases:
        
        fig, ax = plt.subplots(
            nrows=1,
            ncols=5,
            figsize=(29, 12),
            constrained_layout=True
        )
        axs = ax.flatten()

        #for i, ((codes, period), df_period) in enumerate(df_moran_labels.groupby(['codes', 'period'])):
        for i, (period, df_period) in enumerate(df_moran_labels.groupby(['period'])):

            df_slice = df_period[df_period.codes == codeGroup_i]
            # == Map: ==
            ax = axs[i]

            gdf_moran_labels = pandas.merge(
                shape,
                df_slice,
                on='departamento_id',
                how='right'
            )

            # [ ] Armar la anotacion
            moran_info_df = df_moran[(df_moran['periodo'] == period) & (df_moran['codes'] == codeGroup_i)]
            if len(moran_info_df) > 0:
                moran_I = f"{moran_info_df.reset_index().loc[0]['moran_i']:0.2f}"
                moran_p_sim = moran_info_df.reset_index().loc[0]['p_sim']
            else:
                moran_I = 'NOT-FOUND'
                moran_p_sim = "NOT-FOUND"

            moran_annotation = f'''
                Moran I: {moran_I}
                p-value:{moran_p_sim}
            '''
            ax.text(-57, -55, moran_annotation,
                    size=12,
                    color='#0a0a0f',
                    style='italic')

            # [ ] Re-escribir las etiquetas:
            gdf_moran_labels['label'] = gdf_moran_labels.cluster.replace(rename_labels)

            # [ ] - Armar las paletas
            tracts_palette, edge_palette = __get_palettes(gdf_moran_labels.label)

            # [] - Dibujar
            __plot_map(
                data_shape=gdf_moran_labels,
                background_shape=shape,
                groupby_col='label',
                tracts_palette=tracts_palette,
                edge_palette=edge_palette,
                output_file='-',
                figure_title=f'Period: {period}',
                ax=ax
            )


        # [ ] - Agregar anotaciones:
        fig = plot_utils.annotate_figure(
            fig,
            title=f'Moran Statistics: Percentages of {codeGroup_i} over total stillbirths',
            subtitle='Quinquennial Analysis from 1994 to 2019',
            caption="Source: Ministerio de Salud de la República Argentina",
            authorship="GIBEH IPCSH CENPAT-CONICET"
        )
        fig.patch.set_facecolor('white')
        fig.patch.set_alpha(0.8)

        plt.savefig(f"{str(product)}/clustermap-moran-porcentaje-{codeGroup_i}.png", dpi=300)
        plt.close();
        #plt.show();


# + tags=[]
def by_quinquenios(product, upstream):
    ''' Dibuja una grilla con un mapa departamental de la Argentina por cada quinquenio.
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
            shape,df_period,
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
