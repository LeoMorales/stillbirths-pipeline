#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Reportes provinciales
"""
import glob
from stillbirths_package.reporte import Report


# + tags=[]
def create_annual(product, upstream, rates_param, deceases_codes):
    deceases_codes = sorted(deceases_codes)

    # instantiate report obj
    report = Report(
        "Mortinatos", "Análisis provincial anual",
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
    figure_names = [str(name) for name in sorted(glob.glob(f"{upstream['lineplots_by_years']}/*.png"))]
    for figure_name in figure_names:
        # add lineplots:
        report.add_section(
            '',
            figure_name,
            finish_with_page_break=False
        )

    report.build(str(product))


# + tags=[]
def create_quinquennal(product, upstream, rates_param, deceases_codes):

    deceases_codes = sorted(deceases_codes)
    
    # instantiate report obj
    report = Report(
        "Mortinatos", "Análisis provincial por quinquenios",
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
    figure_names = [str(name) for name in sorted(glob.glob(f"{upstream['lineplots_by_quinquennio']}/*.png"))]
    for figure_name in figure_names:
        # add lineplots:
        report.add_section(
            '',
            figure_name,
            finish_with_page_break=False
        )

    report.build(str(product))
