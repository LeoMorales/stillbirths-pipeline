#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw
"""
import pandas
import glob
from stillbirths_package.utils import REGION_BY_PROVINCE_CODE


def __clean_province_code(code):
    '''Limpia el código de provincia'''
    if code == None: return None
    
    return '0'+str(int(code))\
        if (len(str(int(code))) == 1) else str(int(code))

def get_births(product, raw_births_file):
    # # Nacidos vivos
    df = pandas.read_excel(
        raw_births_file,
        dtype={
            'PROVRES': object,
        }
    )

    # # Limpiar
    # limpiamos las columnas
    df['CUENTA'] = \
        df['CUENTA'].astype('int')
    df.loc[:, 'provincia_id'] = \
        df.loc[:, 'PROVRES'].apply(__clean_province_code)
    df = df.rename(
        columns={'AÑO': 'año', 'CUENTA': 'nacimientos'}
    )
    df['año'] = \
        df['año'].astype(int)

    # obtener nombre de la region
    df['region_nombre'] = df.provincia_id.apply(
        lambda provincia_id: REGION_BY_PROVINCE_CODE.get(provincia_id, None)
    )
    df = df.dropna(subset=['region_nombre'])

    # # Filtrar columnas
    output_df = \
        df\
            [['region_nombre', 'año', 'nacimientos']]      

    # # Agrupar
    output_df = \
        output_df\
            .groupby(['region_nombre', 'año'])\
            .sum()\
            .reset_index()

    # Guardar
    # df.to_csv(str(product['data']), index=False)
    output_df.to_parquet(
        str(product['data']), index=False)

def get_stillbirths(product, raw_stillbirths_file, deceases_codes):
    # # Mortinatos
    raw_df = pandas.read_excel(
        raw_stillbirths_file,
        dtype={
            'JURIREG': int,
            'PROVRES': int,
            'CAUSAMUERCIE10': str,
            'AÑO': int,
        }
    )

    raw_df = raw_df.rename(columns={
        'JURIREG': 'jurisdiccion_codigo',
        'PROVRES': 'provincia_codigo',
        'DEPRES': 'departamento_codigo',
        'CAUSAMUERCIE10': 'codigo_muerte',
        'AÑO': 'año',
        'TIEMGEST': 'tiempo_gestacion',
        'PESOFETO': 'peso_feto',
    })

    raw_df = raw_df[['año', 'provincia_codigo', 'codigo_muerte']]

    # # Limpiar
    df = raw_df.copy()
    df.loc[:, 'provincia_id'] = \
        df.loc[:, 'provincia_codigo'].apply(__clean_province_code)
    df['año'] = \
        df['año']\
            .astype('str')\
            .str\
            .replace('.', '')\
            .replace(
                {
                    '201': 2010,
                    '20': 2000,
                    '98': 1998,
                    '97': 1997,
                    '99': 1999,
                    '0': 2000,
                    '9': 2009,
                    '2033': 2003
                }
            )\
            .astype(int)

    # obtener nombre de la region
    df['region_nombre'] = df.provincia_id.apply(
        lambda provincia_id: REGION_BY_PROVINCE_CODE.get(provincia_id, None)
    )
    df = df.dropna(subset=['region_nombre'])
    df['codigo_muerte'] = df.codigo_muerte.str.strip().str.upper()    
    
    deceases_codes = list(set([code.strip().upper() for code in deceases_codes]))
    df = df[df.codigo_muerte.isin(deceases_codes)]

    # # Agrupar
    output_df = \
        df\
        [['region_nombre', 'año', 'codigo_muerte']]\
        .groupby(['region_nombre', 'año'])\
        .count()\
        .reset_index()\
        .rename(columns={'codigo_muerte': 'fallecimientos'})
    
    # # Guardar
    output_df.to_parquet(
        str(product['data']), index=False)
