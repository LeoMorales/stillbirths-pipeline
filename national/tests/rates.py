# -*- coding: utf-8 -*-
import pandas as pd


def test_annual_rates_merge(product):
    """Comprobamos que al finalizar la tarea, tengamos el dataset con
    la estructura deseada.
    
    | region_nombre |  año  |  nacimientos | fallecimientos | tasa |
    ----------------------------------------------------------------
    """
    df = pd.read_parquet(str(product['data']))
    assert len(df.columns) == 5
    assert 'region_nombre' in df.columns
    assert 'año' in df.columns
    assert 'nacimientos' in df.columns
    assert 'fallecimientos' in df.columns
    assert 'tasa' in df.columns
    region_names = df.region_nombre.unique()
    assert ('NOA' in region_names)\
        & ('NEA' in region_names)\
        & ('Centro' in region_names)\
        & ('Cuyo' in region_names)\
        & ('Patagonia' in region_names)


def test_quinquennial_rates_merge(product):
    """Comprobamos que al finalizar la tarea, tengamos el dataset con
    la estructura deseada.
    
    | region_nombre | periodo | nacimientos | fallecimientos | tasa |
    ----------------------------------------------------------------
    """
    df = pd.read_parquet(str(product['data']))
    assert len(df.columns) == 5
    assert 'region_nombre' in df.columns
    assert 'periodo' in df.columns
    assert 'nacimientos' in df.columns
    assert 'fallecimientos' in df.columns
    assert 'tasa' in df.columns
    region_names = df.region_nombre.unique()
    assert ('NOA' in region_names)\
        & ('NEA' in region_names)\
        & ('Centro' in region_names)\
        & ('Cuyo' in region_names)\
        & ('Patagonia' in region_names)
