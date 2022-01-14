#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw
"""
import pandas


def __clean_province_code(code):
    '''Limpia el código de provincia'''
    return '0'+str(code) if (len(str(code)) == 1) else str(code)

def get_births(product, input_file):
    # # Nacidos vivos
    datos_nacidos_vivos = pandas.read_csv(
        input_file,
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

    # # Proyectar
    birth_data_provinces = \
        birth_data\
            [['provincia_id', 'año', 'nacimientos']]      

    # # Agrupar
    birth_data_provinces = \
        birth_data_provinces\
            .groupby(['provincia_id', 'año'])\
            .sum()\
            .reset_index()
    # Guardar

    # df.to_csv(str(product['data']), index=False)
    birth_data_provinces.to_parquet(
        str(product['data']), index=False)

def get_stillbirths(product, input_file):
    # # Mortinatos
    datos_defunciones_fetales = pandas.read_csv(
        input_file,
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

    # # Agrupar
    decease_data_provinces = \
        decease_data\
        [['provincia_id', 'año', 'CAUSAMUER']]\
        .groupby(['provincia_id', 'año'])\
        .count()\
        .reset_index()\
        .rename(columns={'CAUSAMUER': 'fallecimientos'})
    
    # # Guardar
    decease_data_provinces.to_parquet(
        str(product['data']), index=False)
