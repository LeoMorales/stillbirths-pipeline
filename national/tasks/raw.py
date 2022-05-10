#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw NATIONAL
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

    # obtener nombre de la region solo para eliminar aquellos que no sean referenciables a una región:
    df['region_nombre'] = df.provincia_id.apply(
        lambda provincia_id: REGION_BY_PROVINCE_CODE.get(provincia_id, None)
    )
    df = df.dropna(subset=['region_nombre'])
    
    # limpiar el código de muerte
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


def get_cause_percentages(product, raw_stillbirths_file, deceases_codes):
    '''
    Calcula el porcentaje que representa cada codigo de muerte (sobre el total de muertes en el periodo).
    Los códigos contemplados son los que se encuentran indicados en en deceases_codes.

    TODO: Que la tarea genere dos datasets, uno quinquenal y otro anual.
    
    [In]:
        AÑO  JURIREG  PROVRES  DEPRES CAUSAMUERCIE10  TIEMGEST  PESOFETO  Unnamed: 7 Unnamed: 8  
    0  1994       62       62     NaN            A41      20.0     300.0         NaN        NaN  
    1  1994       62       62     NaN            A41      35.0    2600.0         NaN        NaN  
    2  1994        6        6     NaN            A50      34.0    3050.0         NaN        NaN  
    3  1994        6        6     NaN            A50      33.0    2000.0         NaN        NaN  
    4  1994        6        6     NaN            A50      37.0    3070.0         NaN        NaN  

    [Out]:
        codigo_muerte    count   period     percentage
    0   P02              12680   1994-1998  31.785822
    1   P20              8692    1994-1998  21.788830
    2   P96              5044    1994-1998  12.644139
    3   P95              3574    1994-1998  8.959190
    4   P00              3397    1994-1998  8.515492

    '''
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

    # obtener nombre de la region solo para eliminar aquellos que no sean referenciables a una región:
    df['region_nombre'] = df.provincia_id.apply(
        lambda provincia_id: REGION_BY_PROVINCE_CODE.get(provincia_id, None)
    )
    df = df.dropna(subset=['region_nombre'])
    df['codigo_muerte'] = df.codigo_muerte.str.strip().str.upper()    
    
    deceases_codes = list(set([code.strip().upper() for code in deceases_codes]))
    df = df[df.codigo_muerte.isin(deceases_codes)]

    # No agrupar como para la tarea _rates_, obtener porcentajes por c/codigo
    
    # - add periods
    periods = {
        '1994-1998': [1994, 1995, 1996, 1997, 1998],
        '1999-2003': [1999, 2000, 2001, 2002, 2003],
        '2004-2008': [2004, 2005, 2006, 2007, 2008],
        '2009-2013': [2009, 2010, 2011, 2012, 2013],
        '2014-2019': [2014, 2015, 2016, 2017, 2018, 2019],
    }

    df['period'] = df['año'].apply(lambda year: [p for p, y in periods.items() if (year in y)][0])

    # - get the amount for each period
    dfs = []
    for period_i, df_period_i in df.groupby('period'):
        df_period_i_by_codes = \
            df_period_i\
                .codigo_muerte.value_counts()\
                .reset_index()\
                .rename(columns=dict(
                    codigo_muerte='count',
                    index='codigo_muerte'
                ))
        
        df_period_i_by_codes['period'] = period_i

        period_total = df_period_i_by_codes['count'].sum()
        df_period_i_by_codes['percentage'] = df_period_i_by_codes['count'] * 100 / period_total
        # append to a list
        dfs.append(df_period_i_by_codes)

    df_output = pandas.concat(dfs).reset_index(drop=True)   

    # Guardar
    df_output.to_parquet(str(product), index=False)


