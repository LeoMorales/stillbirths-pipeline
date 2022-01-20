# -*- coding: utf-8 -*-
import pandas as pd


def test_births_clean(product):
    """Comprobamos que al finalizar la tarea, tengamos el dataset con
    la estructura deseada.
    
    | region_nombre |  año  |  nacimientos |
    ----------------------------------------
    """
    df = pd.read_parquet(str(product['data']))
    assert len(df.columns) == 3
    assert 'region_nombre' in df.columns
    assert 'año' in df.columns
    assert 'nacimientos' in df.columns
    region_names = df.region_nombre.unique()
    assert ('NOA' in region_names)\
        & ('NEA' in region_names)\
        & ('Centro' in region_names)\
        & ('Cuyo' in region_names)\
        & ('Patagonia' in region_names)

def test_stillbirths_clean(product):
    """Comprobamos que al finalizar la tarea, tengamos el dataset con
    la estructura deseada.
    
    | region_nombre |  año  |  fallecimientos |
    -------------------------------------------
    """
    df = pd.read_parquet(str(product['data']))
    assert len(df.columns) == 3
    assert 'region_nombre' in df.columns
    assert 'año' in df.columns
    assert 'fallecimientos' in df.columns
    region_names = df.region_nombre.unique()
    assert ('NOA' in region_names)\
        & ('NEA' in region_names)\
        & ('Centro' in region_names)\
        & ('Cuyo' in region_names)\
        & ('Patagonia' in region_names)    
