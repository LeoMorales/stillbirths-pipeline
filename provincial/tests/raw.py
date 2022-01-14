import pandas as pd


def test_births_clean(product):
    """Tests for transform.py
    """
    df = pd.read_parquet(str(product['data']))
    assert len(df.columns) == 3
    assert 'provincia_id' in df.columns
    assert 'año' in df.columns
    assert 'nacimientos' in df.columns
    
def test_stillbirths_clean(product):
    """Tests for transform.py
    """
    df = pd.read_parquet(str(product['data']))
    assert len(df.columns) == 3
    assert 'provincia_id' in df.columns
    assert 'año' in df.columns
    assert 'fallecimientos' in df.columns