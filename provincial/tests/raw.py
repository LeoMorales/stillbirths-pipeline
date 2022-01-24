# -*- coding: utf-8 -*-
import pandas as pd


def test_births_clean(product):
    """Tests for transform.py
    """
    df = pd.read_parquet(str(product['data']))
    assert len(df.columns) == 3
    assert 'provincia_id' in df.columns
    assert 'año' in df.columns
    assert 'nacimientos' in df.columns
    # comprobar que todos los códigos de provincia tengan dos caracteres:
    assert len(df.provincia_id.str.len().unique()) == 1
    assert df.provincia_id.str.len().unique()[0] == 2
    # comprobar el rango de años:
    assert df['año'].min() == 1994
    assert df['año'].max() == 2019

def test_stillbirths_clean(product):
    """Tests for transform.py
    """
    df = pd.read_parquet(str(product['data']))
    assert len(df.columns) == 3
    assert 'provincia_id' in df.columns
    assert 'año' in df.columns
    assert 'fallecimientos' in df.columns
    # comprobar que todos los códigos de provincia tengan dos caracteres:
    assert len(df.provincia_id.str.len().unique()) == 1
    assert df.provincia_id.str.len().unique()[0] == 2
    # comprobar el rango de años:
    assert df['año'].min() == 1994
    assert df['año'].max() == 2019
