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
# -

# PROVINCE_NAME_BY_ID = {idProvince: nameProvince for _, (idProvince, nameProvince) in shape[['provincia_id', 'provincia_nombre']].iterrows()}
PROVINCE_NAME_BY_ID = {
    '02': 'CIUDAD DE BUENOS AIRES',
    '06': 'BUENOS AIRES',
    '10': 'CATAMARCA',
    '14': 'CORDOBA',
    '18': 'CORRIENTES',
    '22': 'CHACO',
    '26': 'CHUBUT',
    '30': 'ENTRE RIOS',
    '34': 'FORMOSA',
    '38': 'JUJUY',
    '42': 'LA PAMPA',
    '46': 'LA RIOJA',
    '50': 'MENDOZA',
    '54': 'MISIONES',
    '58': 'NEUQUEN',
    '62': 'RIO NEGRO',
    '66': 'SALTA',
    '70': 'SAN JUAN',
    '74': 'SAN LUIS',
    '78': 'SANTA CRUZ',
    '82': 'SANTA FE',
    '86': 'SANTIAGO DEL ESTERO',
    '90': 'TUCUMAN',
    '94': 'TIERRA DEL FUEGO'
}


# + tags=[]
def by_quinquennios(product, upstream):
    # read data
    #df_upstream = pandas.read_parquet('../_products/rates/rates-by-quinquenios.parquet')
    df_upstream = pandas.read_parquet(upstream['get_quinquenial']['data'])

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
        lambda i: PROVINCE_NAME_BY_ID.get(i, '-')
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


# -
def by_years(product, upstream):
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
        lambda i: PROVINCE_NAME_BY_ID.get(i, '-')
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
