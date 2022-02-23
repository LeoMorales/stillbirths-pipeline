#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw
"""
import pandas
import glob

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

def get_stillbirths(product, raw_stillbirths_folder):
    # # Mortinatos
    raw_df = pandas.DataFrame()
    for filename in glob.glob(f"{raw_stillbirths_folder}/*.xlsx"):
        raw_data_i = pandas.read_excel(
            filename,
            dtype={
                'MPRORES': int,
                'PROVRES': int,
                'MPROVRES': int,
                'AÑO': int,
                'ANO': int,
            }
        )

        raw_data_i = raw_data_i.rename(columns={
            'MPRORES': 'provincia_codigo',
            'JURIREG': 'jurisdiccion_codigo',
            'PROVRES': 'provincia_codigo',
            'MDEPRES': 'departamento_codigo',
            'MPROVRES': 'provincia_codigo',
            'MPAISRES': 'pais_codigo',
            'AÑO': 'año',
            'JURI': 'jurisdiccion_codigo',
            'ANO': 'año',
            'DEPRES': 'departamento_codigo',
            'CODMUER': 'codigo_muerte',
            'CAUSAMUER': 'codigo_muerte',
            'COD': 'codigo_muerte',
            'CAUSAMUERCIE10': 'codigo_muerte',
        })

        raw_data_i = raw_data_i[['año', 'provincia_codigo', 'codigo_muerte']]
        raw_df = pandas.concat(
            [raw_df, raw_data_i])    
    
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
