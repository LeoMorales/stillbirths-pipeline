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


# + tags=[]
def by_quinquennios(product, upstream):
    # read data
    #df_upstream = pandas.read_parquet('../_products/rates/rates-by-quinquenios.parquet')
    df_upstream = pandas.read_parquet(upstream['get_quinquenial']['data'])

    # filter and pivot
    df = df_upstream\
        [['region_nombre', 'periodo', 'tasa']]\
        .pivot(
            index='region_nombre',
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
    df = df.rename(columns=dict(index='region_nombre'))

    # asignar el nombre de provincia como index (para el formateo final de las tasas)
    df = df.set_index(df.region_nombre)
    df = df.drop(columns=['region_nombre'])

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


# -
def by_years(product, upstream):
    # read data
    #df_upstream = pandas.read_parquet('../_products/rates/rates-by-year.parquet')
    df_upstream = pandas.read_parquet(upstream['get_annual']['data'])

    # filter and pivot
    df = df_upstream\
        [['region_nombre', 'año', 'tasa']]\
        .pivot(
            index='region_nombre',
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
