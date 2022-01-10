#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plot births
"""
import pandas
import geopandas
import matplotlib.pyplot as plt
import seaborn
import os
import shutil
import pdfkit
from pandas_profiling import ProfileReport

# + tags=["parameters"]
upstream = ["get_births"]
product = None
# -

# create a temp folder
TMP_FOLDER_DIR = './plot-births-tmp-data'
if not os.path.isdir(TMP_FOLDER_DIR):
    os.mkdir(TMP_FOLDER_DIR)

# # Capa departamentos
# Capa del mapa de Argentina por departamentos.

# +
DEPARTAMENTS_SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson'
departments_shape = geopandas.read_file(DEPARTAMENTS_SHAPE_DIR)
departments_shape = departments_shape[[
    'departamento_id', 'departamento_nombre',
    'provincia_id', 'provincia_nombre',
    'region_indec', 'geometry']]
departments_shape.head()

f, ax = plt.subplots(figsize=(4, 6))
departments_shape.plot(
    ax=ax,
    column='region_indec',
    categorical=True,
    edgecolor='none',
    linewidth=0.02,
)
ax.axis('off')
plt.show();
# -

# # Nacimientos por departamento

df = pandas.read_parquet(upstream['get_births']['data'])
df.head()

# # Mapa

# + endofcell="--"
YEAR = 1994
cmap = seaborn.diverging_palette(250, 5, as_cmap=True)
f, ax = plt.subplots(figsize=(6, 8), constrained_layout=True)
departments_shape.plot(
    ax=ax,
    color='black'
)
pandas.merge(
    departments_shape,
    df[df['año'] == YEAR],
    on='departamento_id'
).plot(
    ax=ax,
    column='nacimientos',
    cmap=cmap,
    edgecolor='none',
    linewidth=0.02,
    legend=True,
    legend_kwds={'shrink': 0.6}
)
ax.axis('off')
ax.set_title(
    f"Nacimientos por departamento\nAño: {YEAR}",
    fontdict={'fontsize': '12', 'fontweight' : '3'}
)
# create an annotation for the data source
ax.annotate(
    'Source: Fuente 2021',
    xy=(0.1,.08),
    xycoords='figure fraction',
    horizontalalignment='left',
    verticalalignment='top',
    fontsize=8,
    color='#555555'
)
MAP_PNG_DIR = f'{TMP_FOLDER_DIR}/test_map.png'
plt.savefig(MAP_PNG_DIR, dpi=300)
plt.close();
# -
# --

# # Lineplot

# Plotting births by year for an specifict department
DEPARTMENT_ID = df\
    .groupby('departamento_id').sum()\
    .reset_index()\
    .sort_values(by='nacimientos', ascending=False)\
    .reset_index(drop=True)\
    .at[10, 'departamento_id']
df_temp = df[df.departamento_id == DEPARTMENT_ID]
fig = plt.figure()
sns_plot = seaborn.lineplot(
    data=df_temp,
    x='año',
    y='nacimientos',
    markers=True,
    dashes=False
)
sns_plot.set_title(
    f'Nacimientos para el departamento {DEPARTMENT_ID}',
    fontsize=20
)
sns_plot.set_xlabel('Año', fontsize=14)
sns_plot.set_ylabel('Nacidos', fontsize=14)
sns_plot.set_xticklabels(df_temp['año'], rotation=20)
sns_plot.grid(True)
sns_plot.legend(labels=['Nacimientos'])
fig.set_size_inches(12, 6)
BIRTHS_PNG_DIR = f"{TMP_FOLDER_DIR}/test_plot.png"
sns_plot.figure.savefig(
    BIRTHS_PNG_DIR, 
    dpi=300, facecolor='w', 
    orientation='portrait',
    bbox_inches='tight')
plt.close()

from IPython.display import Image
Image(filename=BIRTHS_PNG_DIR)

# HTML template to add our data and plots
report_template = '''
<!DOCTYPE html>
    <html>
      <head>
        <meta charset='utf-8'>
        <title>Plot births report</title>
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
          size: 7in 9.25in;
          margin: 27mm 16mm 27mm 16mm;
          }}
          </style>                       
      </head>
      <h1 align="center">Nacimientos</h1>
      <h2 align="center">Reporte de prueba</h2>
'''
def get_fig_template(fig_src: str, width: int, height: int):
    return f'''
        <figure>
        <img src="{fig_src}" width="{width}" height="{height}">
        </figure>
    '''
close_tag = '''
    </html>
'''

# add figures to report:
report_template += get_fig_template(MAP_PNG_DIR, 1000, 1200)
report_template += get_fig_template(BIRTHS_PNG_DIR, 1200, 600)
# close
report_template += close_tag

# Save HTML string to file
HTML_REPORT_DIR = "test_report_birth.html"
with open(HTML_REPORT_DIR, "w") as r:
    r.write(report_template)
#Use pdfkit to create the pdf report from the 
pdfkit.from_file(
    HTML_REPORT_DIR,
     str(product['data'])
) 

# remove the tmp data
os.remove(HTML_REPORT_DIR)
shutil.rmtree(TMP_FOLDER_DIR)
