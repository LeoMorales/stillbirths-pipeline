#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Plot departamental rates by years
"""
import matplotlib.pyplot as plt
import os
import pdfkit
import glob
import PIL

# + tags=["parameters"]
upstream = ["maps_by_years", "lineplots_by_years"]
product = None
rates_param = None


# +
def __get_report_template():
    return f'''
    <!DOCTYPE html>
        <html>
            <head>
                <meta charset='utf-8'>
                <title>PDF - Tasas departamentales por año</title>
                <link rel='stylesheet' href='report.css'>
                <style>
                    h1 {{
                        font-family: Arial;
                        font-size: 300%;
                    }}
                    h2 {{
                        font-family: Arial;
                        font-size: 200%;
                    }}
                    @page {{
                        size: 17in 20in;
                        margin: 27mm 16mm 27mm 16mm;
                    }}
                </style>                       
            </head>
            <h1 align="center">Reporte tasas</h1>
    '''


def __get_fig_template(fig_src: str, width: int, height: int) -> str:
    # guardamos la ultima partecita del nombre
    file_name = fig_src.split('/')[-1]
    file_name = f".../{file_name}"
    return f'''
        <figure>
            <img src="{fig_src}" width="{width}" height="{height}">
            <p align="right">{file_name}</p>
        </figure>
    '''



# + tags=[]
def create(product, upstream, rates_param):

    report_content = __get_report_template()
    # add maps:
    report_content += f'''
        <h2 align="center">Mapas anuales</h2>
        <p align="center">Cantidad de casos sobre {rates_param} nacimientos</p>
    '''
    report_content += __get_fig_template(str(upstream['maps_by_years']), 1200, 1200)

    # add lineplots:
    report_content += f'''
        <div style = "display:block; clear:both; page-break-after:always;"></div>
        <h2 align="center">Tasas anuales por departamentos</h2>
        <p align="center">Cantidad de casos sobre {rates_param} nacimientos</p>
    '''

    # add map figures:
    figure_names = [str(name) for name in sorted(glob.glob(f"{upstream['lineplots_by_years']}/*.png"))]

    FIGURE_MAX_WIDTH = 1200
    for figure_name in figure_names:
        # add figures to report:
        image = PIL.Image.open(figure_name)
        width, height = image.size
        # achicar el ancho de la fihura según la relación
        # ancho de la figura - ancho máximo
        height_max = height * (FIGURE_MAX_WIDTH / width)
        if height_max < height:
            height = height_max
        report_content += __get_fig_template(figure_name, FIGURE_MAX_WIDTH, height)


    # close
    report_content += '''
        </html>
    '''

    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None
    }

    # Save HTML string to file
    HTML_REPORT_DIR = "tmp_report_years.html"
    with open(HTML_REPORT_DIR, "w") as r:
        r.write(report_content)
    #Use pdfkit to create the pdf report from the 
    pdfkit.from_file(
        HTML_REPORT_DIR,
        str(product),
        options=options
    ) 

    # remove the tmp data
    os.remove(HTML_REPORT_DIR)
