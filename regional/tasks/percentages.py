#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Percentages
"""
import pandas
import glob
from stillbirths_package.utils import REGION_BY_PROVINCE_CODE


def __clean_province_code(code):
    '''Limpia el código de provincia'''
    if code == None: return None
    
    return '0'+str(int(code))\
        if (len(str(int(code))) == 1) else str(int(code))

def clean(product, raw_stillbirths_file, deceases_codes):
    '''
    Calcula el porcentaje que representa cada codigo de muerte (sobre el total de muertes en el periodo)
    
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

    # obtener nombre de la region
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

    # Guardar
    df.to_parquet(
        str(product['data']), index=False)


def get_quinquenal_national_level(product, upstream):
    '''
    Calcula el porcentaje que representa cada codigo de muerte (sobre el total de muertes en el periodo)
    
        codigo_muerte    count   period     percentage
    0   P02              12680   1994-1998  31.785822
    1   P20              8692    1994-1998  21.788830
    2   P96              5044    1994-1998  12.644139
    3   P95              3574    1994-1998  8.959190
    4   P00              3397    1994-1998  8.515492

    '''
    # =====
    # Data
    df = pandas.read_parquet(upstream['clean']['data'])

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

    df_country = pandas.concat(dfs).reset_index(drop=True)   
    
    # # Guardar
    df_country.to_parquet(
        str(product['data']), index=False)


def get_quinquenal_regional_level(product, upstream):
    '''
    Calcula el porcentaje que representa cada codigo de muerte (sobre el total de muertes en el periodo)
    
        codigo_muerte   count   region  period      percentage
    0   P02             7269    Centro  1994-1998   33.570406
    1   P20             5923    Centro  1994-1998   27.354177
    2   P96             1957    Centro  1994-1998   9.038009
    3   P00             1850    Centro  1994-1998   8.543851
    4   P01             1047    Centro  1994-1998   4.835358
    '''
    #raw_stillbirths_file = '/home/lmorales/work/stillbirth-book/datasets/defunciones-data-salud/Defunciones fetales 1994 2019 AHORA SI.xlsx'
    #deceases_codes = ['A20', 'A34', 'A41', 'A50']
    
    # =====
    # Data
    df = pandas.read_parquet(upstream['clean']['data'])

    # - get the amount for each period
    dfs = []
    for (region_i, period_i), df_period_i in df.groupby(['region_nombre', 'period']):

        df_period_i_by_codes = \
            df_period_i\
                .codigo_muerte.value_counts()\
                .reset_index()\
                .rename(columns=dict(
                    codigo_muerte='count',
                    index='codigo_muerte'
                ))

        df_period_i_by_codes['region'] = region_i
        df_period_i_by_codes['period'] = period_i

        period_total = df_period_i_by_codes['count'].sum()
        df_period_i_by_codes['percentage'] = df_period_i_by_codes['count'] * 100 / period_total
        
        # append to list:
        dfs.append(df_period_i_by_codes)

    df_regions = pandas.concat(dfs).reset_index(drop=True)

    # # Guardar
    df_regions.to_parquet(
        str(product['data']), index=False)


