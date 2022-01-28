# -*- coding: utf-8 -*-
import pandas as pd


def test_births_clean(product):
    """Tests for get_births
    """
    df = pd.read_parquet(str(product['data']))
    assert len(df.columns) == 3
    assert 'departamento_id' in df.columns
    assert 'año' in df.columns
    assert 'nacimientos' in df.columns
    # comprobar que todos los códigos de departamento tengan dos caracteres:
    assert len(df.departamento_id.str.len().unique()) == 1
    assert df.departamento_id.str.len().unique()[0] == 5
    # comprobar el rango de años:
    assert df['año'].max() == 2019

def test_stillbirths_clean(product):
    """Tests for transform.py
    """
    df = pd.read_parquet(str(product['data']))
    assert len(df.columns) == 3
    assert 'departamento_id' in df.columns
    assert 'año' in df.columns
    assert 'fallecimientos' in df.columns
    # comprobar que todos los códigos de departamento tengan dos caracteres:
    assert len(df.departamento_id.str.len().unique()) == 1
    assert df.departamento_id.str.len().unique()[0] == 5
    # comprobar el rango de años:
    assert df['año'].max() == 2019
