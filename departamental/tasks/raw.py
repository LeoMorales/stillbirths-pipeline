#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw DEPARTAMENTAL
"""
import pandas
import glob
from stillbirths_package.utils import REGION_BY_PROVINCE_CODE


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
    ''' Procesa el dataset de crudo de nacimientos.
    
    Args:
        raw_births_file (str): Route to excel file
            Tiene la siguiente forma:
                AÑO     PROVRES DEPRES  CUENTA
            0   1994.0  2.0     1.0     1380.0
            1   1994.0  2.0     2.0     1321.0
            2   1994.0  2.0     3.0      881.0

    Returns:
        pandas.DataFrame (saves a parquet file).
        
                departamento_id     año     nacimientos
            0   02000               1996    40
            1   02000               1997    24
            2   02000               1998    31
    '''
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

def get_stillbirths(product, raw_stillbirths_file, deceases_codes):
    ''' Procesa el dataset de crudo de nacimientos.
    
    Args:
        raw_births_file (str): Route to excel file
            Tiene la siguiente forma:
               AÑO     JURIREG  PROVRES  DEPRES CAUSAMUERCIE10  TIEMGEST  PESOFETO  Unnamed: 7 Unnamed: 8  
            0  1994.0  62.0     62.0     NaN            A41     20.0         300.0  NaN        NaN  
            1  1994.0  62.0     62.0     NaN            A41     35.0        2600.0  NaN        NaN  
            2  1994.0  6.0      6.0      NaN            A50     34.0        3050.0  NaN        NaN  


    Returns:
        pandas.DataFrame (saves a parquet file).
        
              departamento_id   año  fallecimientos
            0           02000  2006               6
            1           02000  2007               8
            2           02000  2010               4
            3           02001  1997              12
            4           02001  1998              12
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

    raw_df = raw_df[['año', 'provincia_codigo', 'departamento_codigo', 'codigo_muerte']]

    # # Limpiar
    df = raw_df.copy()

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

    df['codigo_muerte'] = df.codigo_muerte.str.strip().str.upper()    

    deceases_codes = list(set([code.strip().upper() for code in deceases_codes]))
    df = df[df.codigo_muerte.isin(deceases_codes)]

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


def get_percentage_for_each_cause(product, raw_stillbirths_file, deceases_codes):
    '''
    Calcula el porcentaje que representa cada codigo de muerte (sobre el total de muertes en el periodo),
    en cada departamento de la Argentina.
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

       codigo_muerte  count     period department_id  percentage
    0            P20      7  1994-1998         02001   58.333333
    4            P20     13  1994-1998         02002   56.521739
    11           P20      8  1994-1998         02003   80.000000
    14           P20     13  1994-1998         02004   92.857143
    16           P20     10  1994-1998         02005   52.631579

    '''
    #raw_stillbirths_file = '/home/lmorales/work/stillbirth-book/datasets/defunciones-data-salud/Defunciones fetales 1994 2019 AHORA SI.xlsx'
    #deceases_codes = ['A20', 'A34', 'A41', 'A50', 'A52', 'A53', 'B24', 'B57', 'B58', 'C34', 'C41', 'C55', 'C91', 'C96', 'D16', 'D18', 'D26', 'D37', 'D38', 'D39', 'D41', 'D43', 'D44', 'D48', 'D56', 'D68', 'D69', 'D70', 'D72', 'D82', 'E03', 'E14', 'E66', 'G71', 'G91', 'I42', 'I49', 'J00', 'J06', 'K46', 'K71', 'K76', 'K83', 'K86', 'N04', 'NC', 'O01', 'O02', 'O03', 'O05', 'O06', 'O07', 'O10', 'O13', 'O14', 'O15', 'O16', 'O20', 'O23', 'O24', 'O25', 'O26', 'O28', 'O31', 'O36', 'O40', 'O41', 'O42', 'O43', 'O45', 'O60', 'O62', 'O64', 'O66', 'O71', 'O74', 'O80', 'O89', 'O90', 'P00', 'P01', 'P02', 'P03', 'P04', 'P05', 'P07', 'P08', 'P10', 'P11', 'P12', 'P13', 'P15', 'P20', 'P21', 'P22', 'P23', 'P24', 'P25', 'P26', 'P28', 'P29', 'P35', 'P36', 'P37', 'P38', 'P39', 'P50', 'P52', 'P53', 'P54', 'P55', 'P56', 'P58', 'P59', 'P60', 'P61', 'P64', 'P70', 'P71', 'P72', 'P74', 'P75', 'P76', 'P77', 'P78', 'P80', 'P83', 'P90', 'P91', 'P93', 'P94', 'P95', 'P96', 'P99', 'Q00', 'Q01', 'Q02', 'Q03', 'Q04', 'Q05', 'Q06', 'Q07', 'Q15', 'Q16', 'Q17', 'Q18', 'Q20', 'Q21', 'Q22', 'Q23', 'Q24', 'Q25', 'Q26', 'Q27', 'Q28', 'Q30', 'Q31', 'Q32', 'Q33', 'Q34', 'Q35', 'Q36', 'Q37', 'Q38', 'Q39', 'Q40', 'Q41', 'Q42', 'Q43', 'Q44', 'Q45', 'Q51', 'Q52', 'Q55', 'Q60', 'Q61', 'Q62', 'Q63', 'Q64', 'Q65', 'Q67', 'Q68', 'Q69', 'Q71', 'Q73', 'Q74', 'Q75', 'Q76', 'Q77', 'Q78', 'Q79', 'Q80', 'Q82', 'Q86', 'Q87', 'Q89', 'Q90', 'Q91', 'Q92', 'Q93', 'Q95', 'Q96', 'Q97', 'Q98', 'Q99', 'R09', 'R95', 'R98', 'R99', 'T62', 'T98', 'V49', 'V89', 'X59', 'Y08', 'Y09', 'Y66']

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

    raw_df = raw_df[['año', 'provincia_codigo', 'departamento_codigo', 'codigo_muerte']]

    # # Limpiar
    df = raw_df.copy()
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

    # obtener nombre de la region
    #df['region_nombre'] = df.provincia_id.apply(lambda provincia_id: REGION_BY_PROVINCE_CODE.get(provincia_id, None))
    df = df.dropna(subset=['departamento_id'])

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

    df['periodo'] = df['año'].apply(lambda year: [p for p, y in periods.items() if (year in y)][0])

    # - get the amount for each period
    dfs = []
    for (period_i, department_i), df_slice in df.groupby(['periodo', 'departamento_id']):
        df_slice_i = \
            df_slice\
                .codigo_muerte.value_counts()\
                .reset_index()\
                .rename(columns=dict(
                    codigo_muerte='cantidad',
                    index='codigo_muerte'
                ))

        df_slice_i['periodo'] = period_i
        df_slice_i['departamento_id'] = department_i

        period_total = df_slice_i['cantidad'].sum()
        df_slice_i['porcentaje_en_departmento'] = df_slice_i['cantidad'] * 100 / period_total
        # append to a list
        dfs.append(df_slice_i)

    df_output = pandas.concat(dfs).reset_index(drop=True)   
    ordered_cols = ['codigo_muerte', 'departamento_id', 'porcentaje_en_departmento', 'periodo', 'cantidad']
    # Guardar
    df_output[ordered_cols].to_parquet(str(product), index=False)



