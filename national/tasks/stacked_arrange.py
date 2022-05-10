#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raw
"""
import pandas
from pathlib import Path
import shutil
from stillbirths_package.utils import GROUP_CODES as BARS_AND_CODES


# + active=""
# BARS_AND_CODES = {
#     "P00-P04": ["P00", "P01", "P02", "P03", "P04"],
#     "P95": ["P95"],
#     "P20": ["P20"],
#     "A50": ["A50"],
#     "Q00-Q99": ['Q00', 'Q01', 'Q02', 'Q03', 'Q04', 'Q05', 'Q06', 'Q07', 'Q15', 'Q16', 'Q17', 'Q18', 'Q20', 'Q21', 'Q22', 'Q23', 'Q24', 'Q25', 'Q26', 'Q27', 'Q28', 'Q30', 'Q31', 'Q32', 'Q33', 'Q34', 'Q35', 'Q36', 'Q37', 'Q38', 'Q39', 'Q40', 'Q41', 'Q42', 'Q43', 'Q44', 'Q45', 'Q51', 'Q52', 'Q55', 'Q60', 'Q61', 'Q62', 'Q63', 'Q64', 'Q65', 'Q67', 'Q68', 'Q69', 'Q71', 'Q73', 'Q74', 'Q75', 'Q76', 'Q77', 'Q78', 'Q79', 'Q80', 'Q82', 'Q86', 'Q87', 'Q89', 'Q90', 'Q91', 'Q92', 'Q93', 'Q95', 'Q96', 'Q97', 'Q98', 'Q99'],
# }
# -

def __arrange_df(df, featuredBarCodes):
    '''
    Reacomoda el dataframe de registro de enfermedades.
    
    Args:
    
        df (pandas.Dataframe): Dataframe de registros individuales
            Tiene la siguiente forma:

                codigo_muerte   count   period      percentage
            0   P02             12680   1994-1998   31.785822
            1   P20             8692    1994-1998   21.788830
            2   P96             5044    1994-1998   12.644139
            [...]
        
        
        featuredBarCodes (dict): Reescritura (clave) y lista de etiquetas que contempla (valor). 
            Ej:
            
            {
                "P00-P04": ["P00", "P01", "P02", "P03", "P04"],
                "P95": ["P95"],
                "P20": ["P20"],
            }
    
    Returns:
        pandas.Dataframe:
        
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


def get_national_quinquennial(product, upstream):
    ''' An intermediate step to save the reordered df to disk.'''
    #df = pandas.read_parquet('../_products/percentages/percentages_country_quinquenal.parquet')
    df = pandas.read_parquet(upstream['raw__get_cause_percentages_quinquennial'])
    
    # con los nuevos códigos segun el dict, reescribir
    df['code'] = __rewrite_codes(df['codigo_muerte'], BARS_AND_CODES)   
    
    # reordenar
    cols_order = ['codigo_muerte', 'period', 'count', 'percentage']
    df = df\
        .drop(columns='codigo_muerte')\
        .groupby(['period', 'code']).sum()\
        .reset_index()\
        .rename(columns=dict(code='codigo_muerte'))\
        [cols_order]

    # get the codes with the highest percentage
    # mainCodes = df[df.period == '1994-1998'].sort_values(by='percentage', ascending=False).loc[:4].codigo_muerte.values
    barCategories = list(BARS_AND_CODES.keys())
    arranged_df = __arrange_df(df, barCategories)
    arranged_df.to_parquet(str(product))

# + active=""
# import pandas
#
# df = pandas.read_parquet('../_products/percentages/percentages_country_quinquenal.parquet')
#
# df.head()
