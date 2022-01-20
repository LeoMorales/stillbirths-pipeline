#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw
"""
import pandas

REGION_BY_PROVINCE_CODE = {
    '38': 'NOA',
    '66': 'NOA',
    '34': 'NEA',
    '22': 'NEA',
    '10': 'NOA',
    '86': 'NOA',
    '54': 'NEA',
    '90': 'NOA',
    '18': 'NEA',
    '46': 'NOA',
    '82': 'Centro',
    '70': 'Cuyo',
    '14': 'Centro',
    '30': 'Centro',
    '74': 'Cuyo',
    '50': 'Cuyo',
    '06': 'Centro',
    '02': 'Centro',
    '42': 'Centro',
    '58': 'Patagonia',
    '62': 'Patagonia',
    '26': 'Patagonia',
    '78': 'Patagonia',
    '94': 'Patagonia'
}


def __clean_province_code(code):
    '''Limpia el código de provincia'''
    return '0'+str(code) if (len(str(code)) == 1) else str(code)

def get_births(product, raw_births_file):
    # # Nacidos vivos
    datos_nacidos_vivos = pandas.read_csv(
        raw_births_file,
        dtype={
            'PROVRES': object,
            'DEPRES': object,
        }
    )
    
    # # Limpiar
    # limpiamos las columnas
    datos_nacidos_vivos['CUENTA'] = \
        datos_nacidos_vivos['CUENTA'].astype('int')
    birth_data = datos_nacidos_vivos.copy()
    birth_data.loc[:, 'provincia_id'] = \
        birth_data.loc[:, 'PROVRES'].apply(__clean_province_code)
    birth_data = birth_data.rename(
        columns={'AÑO': 'año', 'CUENTA': 'nacimientos'}
    )
    birth_data['año'] = \
        birth_data['año']\
            .astype('str')\
            .str\
            .replace('.', '')\
            .replace(
                {'201': 2010, '20': 2000}
            )\
            .astype(int)

    # obtener nombre de la region
    birth_data['region_nombre'] = birth_data.provincia_id.apply(
        lambda provincia_id: REGION_BY_PROVINCE_CODE.get(provincia_id, None)
    )
    birth_data = birth_data.dropna(subset=['region_nombre'])

    # # Filtrar columnas
    birth_data_regions = \
        birth_data\
            [['region_nombre', 'año', 'nacimientos']]      

    # # Agrupar
    birth_data_regions = \
        birth_data_regions\
            .groupby(['region_nombre', 'año'])\
            .sum()\
            .reset_index()

    # Guardar
    # df.to_csv(str(product['data']), index=False)
    birth_data_regions.to_parquet(
        str(product['data']), index=False)

def get_stillbirths(product, raw_stillbirths_file):
    # # Mortinatos
    datos_defunciones_fetales = pandas.read_csv(
        raw_stillbirths_file,
        dtype={'PROVRES': object, 'DEPRES': object}
    )

    # # Limpiar
    decease_data = datos_defunciones_fetales.copy()
    decease_data.loc[:, 'provincia_id'] = \
        decease_data.loc[:, 'PROVRES'].apply(__clean_province_code)
    decease_data = decease_data.rename(
        columns={'AÑO': 'año'}
    )
    decease_data['año'] = \
        decease_data['año']\
            .astype('str')\
            .str\
            .replace('.', '')\
            .replace(
                {'201': 2010, '20': 2000}
            )\
            .astype(int)

    # obtener nombre de la region
    decease_data['region_nombre'] = decease_data.provincia_id.apply(
        lambda provincia_id: REGION_BY_PROVINCE_CODE.get(provincia_id, None)
    )
    decease_data = decease_data.dropna(subset=['region_nombre'])
    
    # # Agrupar
    decease_data_regions = \
        decease_data\
        [['region_nombre', 'año', 'CAUSAMUER']]\
        .groupby(['region_nombre', 'año'])\
        .count()\
        .reset_index()\
        .rename(columns={'CAUSAMUER': 'fallecimientos'})
    
    # # Guardar
    decease_data_regions.to_parquet(
        str(product['data']), index=False)
