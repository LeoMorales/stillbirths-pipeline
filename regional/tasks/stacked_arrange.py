#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stacked arrange datasets
"""
import pandas
from pathlib import Path
import shutil
from stillbirths_package.utils import GROUP_CODES as BARS_AND_CODES


def __arrange_df(df, featuredBarCodes):
    '''
    Convierte el dataframe:
        codigo_muerte   count   period      percentage
    0   P02             12680   1994-1998   31.785822
    1   P20             8692    1994-1998   21.788830
    2   P96             5044    1994-1998   12.644139
    [...]
    
    En el dataframe:
                    P00         P02         P20         P95         P96         Otros
    1994-1998   8.515492    31.785822   21.788830   8.959190    12.644139   16.306528
    1999-2003   8.150058    26.794170   19.593812   27.685994   2.078291    15.697674
    2004-2008   7.386145    22.957024   20.635022   30.519564   3.874278    14.627967
    [...]
    
    Donde P00, P02, P20, P95 y P96 fueron recibidos por parámetro.
    '''
    #df = pandas.read_parquet('../_products/percentages/percentages_country_quinquenal.parquet')
    #df = pandas.read_parquet(upstream['get_quinquenal_national_level']['data'])
   
    # verbose -> observe the order (could be variable):
    periods = ['1994-1998', '1999-2003', '2004-2008', '2009-2013', '2014-2019']
    
    # filtrar los registros que pertenezcan a los periodos seleccionados y que sean de alguno de los códigos con mayor porcentaje:
    featuredBars_df = df[
        (df.period.isin(periods)) &
        (df.codigo_muerte.isin(featuredBarCodes))
    ]

    # ====
    # pivot:
    arranged_df = featuredBars_df.pivot(
        index='period',
        columns='codigo_muerte',
        values='percentage'
    )
    arranged_df.columns.name = None
    arranged_df.index.name = None

    # sumamos los porcentajes del resto de los códigos para dibujar una barra que represente al resto:
    others_df = \
        df[
            (df.period.isin(periods)) &
            ~(df.codigo_muerte.isin(featuredBarCodes))
        ]\
        .groupby(['period'])\
        .sum()\
        .reset_index()

    if len(others_df) > 0:
        others_df = others_df.set_index(others_df.period).drop(columns=['period', 'count'])
        others_df = others_df.rename(columns=dict(percentage='Otros'))
        others_df.index.name = None
        # result:
        #               Otros
        #    1994-1998  16.306528
        #    1999-2003  15.697674
        #    2004-2008  14.627967

        # ====
        # add 'other' column:

        combined_df = pandas.merge(arranged_df.reset_index(), others_df.reset_index())
    
        combined_df.index = combined_df['index']
        combined_df.index.name = None
        combined_df = combined_df.drop(columns='index')
        
        return combined_df
    
    else:
        
        return arranged_df


def __rewrite_codes(values, valuesAndReplacements):
    # valuesAndReplacements es una estructura para reescribir códigos
    response = values.copy()
    for (rewritedValue, valueList) in valuesAndReplacements.items():
        for value in valueList:
            response = response.replace({value: rewritedValue})
    
    return response


def get_regional_quinquenal(product, upstream):
    ''' An intermediate step to save the reordered df to disk.'''
    cols_order = ['codigo_muerte', 'period', 'count', 'percentage']
        
    # ==========
    # data:
    df = pandas.read_parquet(
        upstream['get_regional_percentages_at_quinquenal'])

    # ==========
    # loop:
    dfs = []
    for region_i, df_region_i in df.groupby('region'):

        # con los nuevos códigos segun el dict, reescribir
        df_region_i['code'] = __rewrite_codes(df_region_i['codigo_muerte'], BARS_AND_CODES)   

        # agrupar
        df_region_i = df_region_i\
            .drop(columns='codigo_muerte')\
            .groupby(['period', 'code']).sum()\
            .reset_index()\
            .rename(columns=dict(code='codigo_muerte'))\
            [cols_order]
        
        # re-arrange the regional dataframe:
        arranged_df = __arrange_df(
            df_region_i.reset_index(drop=True),
            list(BARS_AND_CODES.keys())
        )
        
        # add a region column:
        arranged_df['region'] = region_i
        
        # append to a list, then concatenate all
        dfs.append(arranged_df.copy())

    # ==========
    # concat op and save:
    output_df = pandas.concat(dfs).fillna(0.0)
    output_df.to_parquet(str(product))

# + active=""
# import pandas
#
# df = pandas.read_parquet('../_products/percentages/percentages_country_quinquenal.parquet')
#
# df.head()
