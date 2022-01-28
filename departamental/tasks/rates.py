#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get rates (by year)
Merge stillbirths and births
"""
import pandas
from stillbirths_package import tasas


def get_annual(product, upstream, rates_over):
    # # Mortinatos por departamento
    df_stillbirths = pandas.read_parquet(upstream['get_stillbirths']['data'])

    # # Nacimientos por departamento
    df_births = pandas.read_parquet(upstream['get_births']['data'])

    # # Combinar
    df_rates = pandas.merge(
        df_births,
        df_stillbirths,
        on=['departamento_id', 'año'],
        how='left'
    )
    df_rates['fallecimientos'] = \
        df_rates.fallecimientos.fillna(0).astype('int')

    # # Obtener las tasas

    df_rates['tasa'] = \
        tasas.get_tasa(
            df_rates.fallecimientos,
            df_rates.nacimientos,
            rates_over
        )

    # # Guardar

    # df.to_csv(str(product['data']), index=False)
    df_rates.to_parquet(
        str(product['data']), index=False
    )

def get_quinquenial(product, upstream, rates_over):
    # # Mortinatos por departamento
    df_stillbirths = pandas.read_parquet(upstream['get_stillbirths']['data'])

    # # Nacimientos por departamento
    df_births = pandas.read_parquet(upstream['get_births']['data'])
    
    # # Combinar
    df_rates = pandas.merge(
        df_births,
        df_stillbirths,
        on=['departamento_id', 'año'],
        how='left'
    )

    df_rates['fallecimientos'] = \
        df_rates.fallecimientos.fillna(0).astype('int')

    # # Agrupar por quinquenio
    periods = {
        '1994-1998': [1994, 1995, 1996, 1997, 1998],
        '1999-2003': [1999, 2000, 2001, 2002, 2003],
        '2004-2008': [2004, 2005, 2006, 2007, 2008],
        '2009-2013': [2009, 2010, 2011, 2012, 2013],
        '2014-2019': [2014, 2015, 2016, 2017, 2018, 2019],
    }

    # # Obtener las tasas
    df_rates_quinquenal = pandas.DataFrame()
    for i, period in enumerate(periods):
        dataset_i = df_rates\
            [df_rates['año'].isin(periods[period])]\
            .drop(columns=['año'])\
            .groupby(['departamento_id'])\
            .sum()\
            .reset_index()

        dataset_i['tasa'] = \
            tasas.get_tasa(
                dataset_i['fallecimientos'],
                dataset_i['nacimientos'],
                rates_over
            )

        dataset_i['periodo'] = period

        df_rates_quinquenal = pandas.concat([
            df_rates_quinquenal,
            dataset_i
        ])

    # # Guardar
    df_rates_quinquenal.to_parquet(
        str(product['data']), index=False
    )
