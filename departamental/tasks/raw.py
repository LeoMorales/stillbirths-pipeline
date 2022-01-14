#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw
"""
import pandas


def __clean_department_code(code):
    '''Limpia el código de departamento'''
    pad = 3 - len(str(code))
    return '0'*pad + str(code)

def __clean_province_code(code):
    '''Limpia el código de provincia'''
    return '0'+str(code) if (len(str(code)) == 1) else str(code)

def get_births(product, input_file):
    # # Nacidos vivos
    # '../datasets/Copia para Leo_de Nacidos vivos 1994-2019.xlsx - Nacidos vivos 2005-2018.csv'
    datos_nacidos_vivos = pandas.read_csv(
        input_file,
        dtype={
            'PROVRES': object,
            'DEPRES': object,
        }
    )
    # # Limpiar
    # limpiamos las columnas
    datos_nacidos_vivos['CUENTA'] = datos_nacidos_vivos['CUENTA'].astype('int')
    birth_data = datos_nacidos_vivos.copy()
    birth_data.loc[:, 'provincia_id'] = \
        birth_data.loc[:, 'PROVRES'].apply(__clean_province_code)
    birth_data.loc[:, 'departamento_id'] = \
        birth_data.loc[:, 'DEPRES'].apply(__clean_department_code)
    birth_data.loc[:, 'departamento_id'] = \
        birth_data['provincia_id'] + birth_data['departamento_id']
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

    # # Datos departamentales
    # eliminar los registros con DEPRES en null
    birth_data_departments = \
        birth_data\
            [~birth_data.DEPRES.isna()]\
            [['departamento_id', 'año', 'nacimientos']]      

    # Agrupar

    birth_data_departments = \
        birth_data_departments\
            .groupby(['departamento_id', 'año'])\
            .sum()\
            .reset_index()

    # Guardar

    # df.to_csv(str(product['data']), index=False)
    birth_data_departments.to_parquet(
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
    decease_data.loc[:, 'departamento_id'] = \
        decease_data.loc[:, 'DEPRES'].apply(__clean_department_code)
    decease_data.loc[:, 'departamento_id'] = \
        decease_data['provincia_id'] + decease_data['departamento_id']
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
    decease_data_departments = \
        decease_data\
        [~decease_data.DEPRES.isna()]\
        [['departamento_id', 'año', 'CAUSAMUER']]\
        .groupby(['departamento_id', 'año'])\
        .count()\
        .reset_index()\
        .rename(columns={'CAUSAMUER': 'fallecimientos'})

    # # Guardar

    # df.to_csv(str(product['data']), index=False)
    decease_data_departments.to_parquet(
        str(product['data']), index=False)
