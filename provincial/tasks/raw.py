#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw
"""
import pandas
import glob


def __clean_province_code(code):
    '''Limpia el código de provincia'''
    if code == None: return None
    
    return '0'+str(int(code))\
        if (len(str(int(code))) == 1) else str(int(code))

def get_births(product, input_file):
    # # Nacidos vivos
    raw_df = pandas.read_excel(
        input_file,
        dtype={
            'PROVRES': object,
            'DEPRES': object,
        }
    )
    # # Limpiar
    # limpiamos las columnas
    raw_df['CUENTA'] = \
        raw_df['CUENTA'].astype('int')
    df = raw_df.copy()
    df.loc[:, 'provincia_id'] = \
        df.loc[:, 'PROVRES'].apply(__clean_province_code)
    df = df.rename(
        columns={'AÑO': 'año', 'CUENTA': 'nacimientos'}
    )
    df['año'] = \
        df['año'].astype(int)

    # # Proyectar
    output_df = \
        df[['provincia_id', 'año', 'nacimientos']]

    # # Agrupar
    output_df = \
        output_df\
            .groupby(['provincia_id', 'año'])\
            .sum()\
            .reset_index()
    # Guardar

    # df.to_csv(str(product['data']), index=False)
    output_df.to_parquet(
        str(product['data']), index=False)

def get_stillbirths(product, raw_data_folder):
    # # Mortinatos

    #csv_nacimientos_dir = '../../../datasets/nacimientos/'
    raw_df = pandas.DataFrame()
    for filename in glob.glob(f"{raw_data_folder}/*.xlsx"):
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

    # # Agrupar
    output_df = \
        df\
        [['provincia_id', 'año', 'codigo_muerte']]\
        .groupby(['provincia_id', 'año'])\
        .count()\
        .reset_index()\
        .rename(columns={'codigo_muerte': 'fallecimientos'})
    
    # # Guardar
    output_df.to_parquet(
        str(product['data']), index=False)

