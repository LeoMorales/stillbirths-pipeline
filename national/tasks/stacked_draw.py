#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stacked bar charts are drawn here
"""
import pandas
from stillbirths_package import plot_utils


def national_quinquennial(product, upstream):
    df = pandas.read_parquet(upstream['stacked_arrange__get_national_quinquennial'])
    plot_utils.draw_stacked(str(product), df)
