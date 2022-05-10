from stillbirths_package.utils import GROUP_CODES
import pandas


def get_percentages_for_each_code_group(product, upstream):
    '''
    Retorna el acumulado de cada grupo de codigos de defunciones
    especificado en GROUP_CODES.
    
    Args:
    
    Returns:
    
        - pandas.DataFrame:
        
                departamento_id code_group  period      porcentaje_en_departmento
            0   02001           P00-P04     1994-1998   16.666667
            1   02002           P00-P04     1994-1998   26.086957
            2   02003           P00-P04     1994-1998   10.000000
            3   02004           P00-P04     1994-1998   7.142857
            4   02005           P00-P04     1994-1998   31.578947
    '''
    df = pandas.read_parquet(
        upstream['raw__get_percentage_for_each_cause'])

    accumulatedDataframes = []

    # for each period
    for period_i, df_period_i in df.groupby(['periodo']):

        # and then, for each group of codes:
        for codeGroup in GROUP_CODES:

            # [ ] - filter by group 
            df_i = df_period_i[(df_period_i.codigo_muerte.isin(GROUP_CODES[codeGroup]))]

            # [ ] - accumulate percentages
            df_i = df_i\
                .groupby('departamento_id')\
                .sum()\
                .reset_index()

            ordered_columns = ['departamento_id', 'code_group', 'period', 'porcentaje_en_departmento']
            accumulatedDataframes.append(
                df_i
                    .assign(code_group=codeGroup, period=period_i)
                    [ordered_columns]
                    .copy()
            )
    df = pandas.concat(accumulatedDataframes)
    df.to_parquet(str(product), index=False)
