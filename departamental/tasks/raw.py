#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw
"""
import pandas
import glob


def __clean_department_code(code):
    '''Limpia el código de departamento'''
    if pandas.isna(code): return None

    pad = 3 - len(str(int(code)))
    return '0'*pad + str(int(code))

def __clean_province_code(code):
    '''Limpia el código de provincia'''
    if not code: return None
    
    return '0'+str(int(code))\
        if (len(str(int(code))) == 1) else str(int(code))

def get_births(product, raw_births_file):
    # # Nacidos vivos
    # raw_births_file = '/home/lmorales/work/stillbirth-book/datasets/nacidos-vivos-data/Copia para Leo_de Nacidos vivos 1994-2019.xlsx'
    df = pandas.read_excel(
        raw_births_file,
        dtype={
            'PROVRES': int,
            'DEPRES': int,
            'AÑO': int
        }
    )

    # # Limpiar
    # limpiamos las columnas
    df['CUENTA'] = df['CUENTA'].astype('int')
    df.loc[:, 'provincia_id'] = \
        df.loc[:, 'PROVRES'].apply(__clean_province_code)
    df.loc[:, 'departamento_id'] = \
        df.loc[:, 'DEPRES'].apply(__clean_department_code)
    df.loc[:, 'departamento_id'] = \
        df['provincia_id'] + df['departamento_id']
    df = df.rename(
        columns={'AÑO': 'año', 'CUENTA': 'nacimientos'}
    )

    # # Datos departamentales
    # eliminar los registros con DEPRES en null
    output_df = \
        df\
            [~df.DEPRES.isna()]\
            [['departamento_id', 'año', 'nacimientos']]      

    # Agrupar

    output_df = \
        output_df\
            .groupby(['departamento_id', 'año'])\
            .sum()\
            .reset_index()

    # Guardar

    # df.to_csv(str(product['data']), index=False)
    output_df.to_parquet(
        str(product['data']), index=False)

def get_stillbirths(product, raw_stillbirths_folder):
    # # Mortinatos
    #raw_stillbirths_folder = '/home/lmorales/work/stillbirth-book/datasets/defunciones-data-salud/'
    df = pandas.DataFrame()
    for filename in glob.glob(f"{raw_stillbirths_folder}/*.xlsx"):
        raw_data_i = pandas.read_excel(
            filename,
            dtype={
                'MPRORES': int,
                'PROVRES': int,
                'MPROVRES': int,
                'MDEPRES': object,
                'DEPRES': object,
                'AÑO': int,
                'ANO': int,
            }
        )

        raw_data_i = raw_data_i.rename(columns={
            'MPAISRES': 'pais_codigo',
            'JURIREG': 'jurisdiccion_codigo',
            'JURI': 'jurisdiccion_codigo',
            'MPRORES': 'provincia_codigo',
            'PROVRES': 'provincia_codigo',
            'MPROVRES': 'provincia_codigo',
            'MDEPRES': 'departamento_codigo',
            'DEPRES': 'departamento_codigo',
            'AÑO': 'año',
            'ANO': 'año',
            'CODMUER': 'codigo_muerte',
            'CAUSAMUER': 'codigo_muerte',
            'COD': 'codigo_muerte',
        })

        if not ('departamento_codigo' in raw_data_i.columns):
            print(f"{filename}\nNo se encontró código de departamento, columnas: {', '.join(raw_data_i.columns)}")
            continue

        if not ('provincia_codigo' in raw_data_i.columns):
            print(f"{filename}\nNo se encontró código de provincia, columnas: {', '.join(raw_data_i.columns)}")
            continue

        raw_data_i = raw_data_i[['año', 'departamento_codigo', 'provincia_codigo', 'codigo_muerte']]
        df = pandas.concat(
            [df, raw_data_i])    

    # # Limpiar
    df.loc[:, 'provincia_id'] = \
        df.loc[:, 'provincia_codigo'].apply(__clean_province_code)
    df.loc[:, 'departamento_id'] = \
        df.loc[:, 'departamento_codigo'].apply(__clean_department_code)
    df.loc[:, 'departamento_id'] = \
        df['provincia_id'] + df['departamento_id']

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
        [~df.departamento_codigo.isna()]\
        [['departamento_id', 'año', 'codigo_muerte']]\
        .groupby(['departamento_id', 'año'])\
        .count()\
        .reset_index()\
        .rename(columns={'codigo_muerte': 'fallecimientos'})

    # # Guardar

    # df.to_csv(str(product['data']), index=False)
    output_df.to_parquet(
        str(product['data']), index=False)
