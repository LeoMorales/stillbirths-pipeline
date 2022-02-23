#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Plot departamental rates by years
"""
import pandas
import seaborn
import imgkit
from IPython.display import Image, display
from stillbirths_package import utils
from pathlib import Path
import shutil


# -

def by_years(product, upstream):
    ## initial setup (folder product):
    
    parent = Path(product)
    # clean up products from the previous run, if any. Otherwise they'll be
    # mixed with the current files
    if parent.exists():
        shutil.rmtree(parent)
    # make sure the directory exists
    parent.mkdir(exist_ok=True, parents=True)

    # read data
    #df_upstream = pandas.read_parquet('../_products/rates/rates-by-year.parquet')
    df_upstream = pandas.read_parquet(upstream['get_annual']['data'])

    province_ids = df_upstream.departamento_id.str.slice(0, 2).unique()
    df = df_upstream.copy()

    # filter and pivot
    df = df\
        [['departamento_id', 'año', 'tasa']]\
        .pivot(
            index='departamento_id',
            columns='año'
        )

    # clean column and index names
    df.columns.name = None
    df.index.name = None

    df.columns = [
        str(year)
        for _, year
        in df.columns.values
    ]

    # desde el id, obtener el nombre de la provincia
    df['provincia_nombre'] =  df.index.to_series().str.slice(0, 2).apply(
        lambda i: utils.PROVINCE_NAME_BY_ID.get(i, '-')
    )
    # y eliminar aquellas filas sin nombre de provincia
    df = df[df.provincia_nombre != '-']
    index_arrays = [
        df.provincia_nombre.values,
        df.index.values,
    ]
    df = df.set_index(index_arrays)
    df = df.drop(columns='provincia_nombre')

    for i, province_name in enumerate(utils.PROVINCE_NAME_BY_ID.values()):
        df_img = df.loc[province_name].copy()
        df_img['departamento_nombre'] = [utils.DEPARTMENT_NAME_BY_ID.get(id_i, '-') for id_i in df_img.index]
        df_img = df_img[df_img.departamento_nombre != '-']
        df_img.index = df_img['departamento_nombre']
        df_img = df_img.drop(columns='departamento_nombre')

        # crear figura
        province_name_in_path = province_name.replace(' ', '_')
        output_file = f"{str(product)}/{province_name_in_path}.png"
        cmap = seaborn.diverging_palette(250, 5, as_cmap=True)
        BY_ROW = 1
        styled_table = \
            df_img\
                .dropna()\
                .style.background_gradient(
                    cmap=cmap, axis=BY_ROW
                )\
                .format('{0:.2f}')

        html = styled_table.render()
        imgkit.from_string(html, output_file)


def __by_years(product, upstream):
    # read data
    #df_upstream = pandas.read_parquet('../_products/rates/rates-by-year.parquet')
    df_upstream = pandas.read_parquet(upstream['get_annual']['data'])

    # filter and pivot
    df = df_upstream\
        [['provincia_id', 'año', 'tasa']]\
        .pivot(
            index='provincia_id',
            columns='año'
        )

    # clean column and index names
    df.columns.name = None
    df.index.name = None

    df.columns = [
        str(year)
        for _, year
        in df.columns.values
    ]

    # ids provincia  como columna
    df = df.reset_index()
    df = df.rename(columns=dict(index='provincia_id'))

    # desde el id, obtener el nombre de la provincia
    df['provincia_nombre'] = df.provincia_id.apply(
        lambda i: utils.PROVINCE_NAME_BY_ID.get(i, '-')
    )
    # y eliminar aquellas filas sin nombre de provincia
    df = df[df.provincia_nombre != '-']

    # asignar el nombre de provincia como index (para el formateo final de las tasas)
    df = df.set_index(df.provincia_nombre)
    df = df.drop(columns=['provincia_id', 'provincia_nombre'])

    # agregar la fila de valor medio para el año
    mean_row = pandas.DataFrame([df.mean(axis=0).to_dict()])
    mean_row.index = ['Valor medio']
    df = pandas.concat([df, mean_row])
    
    # crear figura
    cmap = seaborn.diverging_palette(250, 5, as_cmap=True)
    BY_ROW = 1
    styled_table = \
        df\
            .dropna()\
            .style.background_gradient(
                cmap=cmap, axis=BY_ROW
            )\
            .format('{0:.2f}')

    html = styled_table.render()
    imgkit.from_string(html, str(product))


# + tags=[]
def by_quinquennios(product, upstream):
    # read data
    #df_upstream = pandas.read_parquet('../_products/rates/rates-by-quinquenios.parquet')
    df_upstream = pandas.read_parquet(
        upstream['get_quinquenial']['data'])

    # filter and pivot
    df = df_upstream\
        [['provincia_id', 'periodo', 'tasa']]\
        .pivot(
            index='provincia_id',
            columns='periodo'
        )

    # clean column and index names
    df.columns.name = None
    df.index.name = None
    df.columns = [
        ''.join(col).strip().replace('tasa', '')
        for col
        in df.columns.values
    ]

    # ids provincia  como columna
    df = df.reset_index()
    df = df.rename(columns=dict(index='provincia_id'))

    # desde el id, obtener el nombre de la provincia
    df['provincia_nombre'] = df.provincia_id.apply(
        lambda i: utils.PROVINCE_NAME_BY_ID.get(i, '-')
    )
    # y eliminar aquellas filas sin nombre de provincia
    df = df[df.provincia_nombre != '-']

    # asignar el nombre de provincia como index (para el formateo final de las tasas)
    df = df.set_index(df.provincia_nombre)
    df = df.drop(columns=['provincia_id', 'provincia_nombre'])

    # agregar la fila de valor medio para el año
    mean_row = pandas.DataFrame([df.mean(axis=0).to_dict()])
    mean_row.index = ['Valor medio']
    df = pandas.concat([df, mean_row])
    
    # crear figura
    cmap = seaborn.diverging_palette(250, 5, as_cmap=True)
    BY_ROW = 1
    styled_table = \
        df\
            .dropna()\
            .style.background_gradient(
                cmap=cmap, axis=BY_ROW
            )\
            .format('{0:.2f}')
    html = styled_table.render()
    imgkit.from_string(html, str(product))
