#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Build reports
"""
import os
from stillbirths_package.reporte import Report
import glob


# + tags=[]
def create_annual(product, upstream, rates_param, deceases_codes):

    deceases_codes = sorted(deceases_codes)
    
    # instantiate report obj
    report = Report(
        "Mortinatos", "Análisis regional anual",
        rates_param, deceases_codes
    )
    
    # add maps:
    report.add_section(
        '<h2 align="center">Mapas por año</h2>',
        str(upstream['maps_by_years']))
    
    # add table:
    report.add_section(
        '<h2 align="center">Tabla de calor</h2>',
        str(upstream['table_by_years'])
    )

    # add lineplots:
    report.add_section(
        '<h2 align="center">Lineplot de tasas anuales por regiones</h2>',
        str(upstream['lineplots_by_years']),
        finish_with_page_break=True
    )

    # add stacked:
    report.add_section(
        '<h2 align="center">Porcentajes por código de defuncion, por regiones</h2>',
        finish_with_page_break=False
    )

    for stackedImage in glob.glob(f"{str(upstream['draw_stacked_regional_quinquenal'])}/*.png"):
        report.add_section(
            '<h3 align="center"></h3>',
            str(stackedImage),
            finish_with_page_break=False
        )

    report.build(str(product))


# + tags=[]
def create_quinquennal(product, upstream, rates_param, deceases_codes):

    deceases_codes = sorted(deceases_codes)
    
    # instantiate report obj
    report = Report(
        "Mortinatos", "Análisis regional por quinquenios",
        rates_param, deceases_codes
    )
    
    # add maps:
    report.add_section(
        '<h2 align="center">Mapas quinquenales</h2>',
        str(upstream['maps_by_quinquenios']))
    
    # add table:
    report.add_section(
        '<h2 align="center">Tabla de calor</h2>',
        str(upstream['table_by_quinquenios'])
    )

    # add lineplots:
    report.add_section(
        '<h2 align="center">Lineplot de tasas quinquenales por regiones</h2>',
        str(upstream['lineplots_by_quinquennio']),
        finish_with_page_break=False
    )

    report.build(str(product))
