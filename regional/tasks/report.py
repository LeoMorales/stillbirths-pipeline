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
import datetime

# +
PDF_EXPORT_OPTIONS = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None,
    'footer-left': "Reporte generado: <report_timestamp>",
    'footer-line':'',
    'footer-font-size':'7',
    'footer-right': '[page] of [topage]'       
}

BR = '<div style="display:block; clear:both; page-break-after:always;"></div>'
IMGS_BASEWITH = 1000


# -

class Report:
    
    def __init__(self, title: str, subtitle: str, rates_param: int, deceases_codes: list):
        self.title = title
        self.subtitle = subtitle
        self.rates_param = rates_param
        self.deceases_codes = deceases_codes
        
        self.tmp_files = []
        self.content = ''

    def add_section(self, text, figure = None, caption = '', finish_with_page_break = True):
        # add section (title, fig, caption):
        
        # > title
        report_content = f"{text}"
        
        # > figure
        if figure:
            RESIZED_IMAGE_DIR, w, h = self.__resize_image(
                figure,
                basewidth=IMGS_BASEWITH
            )
            report_content += self.__get_fig_template(RESIZED_IMAGE_DIR, w, h)
            #report_content += BR
            self.tmp_files.append(RESIZED_IMAGE_DIR)
        
        # > caption
        report_content += caption
        
        if finish_with_page_break:
            report_content += BR
        
        self.content += report_content

    def get_report_text(self):
        return f'''
            <!DOCTYPE html>
                <html>
                    <head>
                        <meta charset='utf-8'>
                        <title>{self.title}</title>
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
                    <body>
                        <div style="margin-top:150px;">
                            <h1 align="center">{self.title}</h1>
                            <h2 align="center">{self.subtitle}</h2>
                            <br>
                            <br>
                            <h3>Parámetros:</h3>
                            <p>Tasa:</p>
                            <ul><li> Mortinatos por cada {self.rates_param} nacimientos vivos </li></ul>
                            <p>Para este reporte se utilizaron los códigos de muertes:</p>
                            <ul><li> {self.deceases_codes} </li></ul>
                        </div>
                        <div style="display:block; clear:both; page-break-after:always;"></div>
                        {self.content}
                    </body>
                </html>
            '''
    
    def build(self, destination):
        # destination = str(product)
        
        # set current time
        PDF_EXPORT_OPTIONS['footer-left'] = f"Reporte generado: {str(datetime.datetime.now())}"
        # Save HTML string to file
        HTML_REPORT_DIR = "tmp_report_years.html"

        with open(HTML_REPORT_DIR, "w") as r:
            r.write(self.get_report_text())

        #Use pdfkit to create the pdf report from the 
        pdfkit.from_file(
            HTML_REPORT_DIR,
            destination,
            options=PDF_EXPORT_OPTIONS
        ) 

        # remove the tmp data
        os.remove(HTML_REPORT_DIR)

    def __resize_image(self, image_path, basewidth):
        input_image = PIL.Image.open(image_path)
        img_width, img_height = input_image.size

        wpercent = (basewidth / float(img_width))
        hsize = int((float(img_height) * float(wpercent)))
        img = input_image.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        base_name = image_path.split('/')[-1].rstrip('.png')
        output_image_path = f'./{base_name}_{datetime.datetime.now().isoformat()}.png'
        img.save(output_image_path)
        
        return output_image_path, basewidth, hsize

    def __get_fig_template(self, fig_src: str, width: int, height: int) -> str:
        return f'''
            <figure align="center">
                <img align="center" src="{fig_src}" width="{width}" height="{height}">
            </figure>
        '''    


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
        finish_with_page_break=False
    )

    report.build(str(product))
    for tmp_file in report.tmp_files:
        print(f"removing {tmp_file}...")
        os.remove(tmp_file)


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
    
    for tmp_file in report.tmp_files:
        print(f"removing {tmp_file}...")
        os.remove(tmp_file)
