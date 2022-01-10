#!/usr/bin/env python
# -*- coding: utf-8 -*-
# + tags=[]
"""
Plot departamental rates by quinquenio
"""
import pandas
import geopandas
import matplotlib.pyplot as plt
import seaborn
import os
import shutil
import pdfkit
from IPython.display import Image
import glob
import PIL

# + tags=["parameters"]
upstream = ["get_quinquenial"]
product = None

# + tags=[]
# create a temp folder
TMP_FOLDER_DIR = './plot-rates-quinquenios-tmp-data'
if not os.path.isdir(TMP_FOLDER_DIR):
    os.mkdir(TMP_FOLDER_DIR)

# + [markdown] tags=[]
# # Leer tasas

# + tags=[]
df = pandas.read_parquet(upstream['get_quinquenial']['data'])
df.head()

# + [markdown] tags=[]
# # Capa departamentos
# Capa del mapa de Argentina por departamentos.

# + tags=[]
DEPARTAMENTS_SHAPE_DIR = '/home/lmorales/work/stillbirth-book/notebooks/shapes/departamentos.geojson'
departments_shape = geopandas.read_file(DEPARTAMENTS_SHAPE_DIR)
departments_shape = departments_shape[[
    'departamento_id', 'departamento_nombre',
    'provincia_id', 'provincia_nombre',
    'region_indec', 'geometry']]
print(departments_shape.head())

f, ax = plt.subplots(figsize=(3, 4))
departments_shape.plot(
    ax=ax,
    column='region_indec',
    categorical=True,
    edgecolor='none',
    linewidth=0.02,
)
ax.axis('off')
plt.show();

# + [markdown] tags=[]
# # Verificación de departamentos

# + [markdown] tags=[]
# Observamos cuales códigos de departamentos de los datos de las tasas no se encuentran en la capa.

# + tags=[]
departments_idx = departments_shape.departamento_id.unique()
print(len(departments_idx))

# filter not in shape idx
print(len(df))
df = df[df.departamento_id.isin(departments_idx)]
print(len(df[df.departamento_id.isin(departments_idx)]))

# + [markdown] tags=[]
# # Mapas

# + [markdown] tags=[]
# Por cada año, dibujamos un mapa

# + tags=[]
cmap = seaborn.diverging_palette(250, 5, as_cmap=True)

ncols, nrows = 5, 1
f, ax = plt.subplots(
    nrows=nrows, ncols=ncols,
    figsize=(26, 10),
    constrained_layout=True
)
axs = ax.flatten()

for i, year_i in enumerate(sorted(list(df['periodo'].unique()))):
    # == Map: ==
    ax = axs[i]
    
    df_periodo_i = df[df['periodo'] == year_i]
    # verificar que no hayan departamentos repetidos
    assert len(df_periodo_i.departamento_id) == len(df_periodo_i.departamento_id.unique())
    
    # black map background:
    departments_shape.plot(
        ax=ax,
        color='black'
    )    
    # main map:
    pandas.merge(
        departments_shape,
        df_periodo_i,
        on='departamento_id'
    ).plot(
        ax=ax,
        column='tasa',
        cmap=cmap,
        edgecolor='none',
        linewidth=0.02,
        legend=True,
        legend_kwds={'shrink': 0.5},
    )
    ax.axis('off')
    ax.set_title(f"Período {year_i}", fontsize=16)

f.suptitle(
    "Tasas departamentales por quinquenio",
    fontsize=20#, y=1.08
)

MAPS_PNG_DIR = f'{TMP_FOLDER_DIR}/maps.png'
plt.savefig(MAPS_PNG_DIR, dpi=300)
plt.close();

Image(filename=MAPS_PNG_DIR)


# + [markdown] tags=[]
# # Lineplots

# + [markdown] tags=[]
# Escribimos una función para dibujar la grilla de evolución de las tasas para los departamentos de una provincia.
#
# La función es útil porque la vamos a utilizar en bucle.

# + tags=[]
def plot_tasas_by_departments(
        df_data, dict_names,
        time_col='año',
        rate_col='tasa',
        hue_col='departamento_id',
        only_save=False,
        figure_name='plot.png',
        figure_title='Plot',
        max_rows=7,
        col_wrap=3,
        verbose=False
    ):
    """
    Con la información de las tasas de una provincia (desagregada por departamento),
    crea la grilla con las lineas de tiempo por cada uno de estos departamentos.
    """
    TOTAL = len(data_provincia_i.departamento_id.unique())
    BASE = 0
    STEP = max_rows * col_wrap
    TOP = STEP
    
    part = 1
    while BASE < TOTAL:
        figure_department_idx = data_provincia_i.departamento_id.unique()[BASE:TOP]
        #print(figure_department_idx)
        BASE += STEP
        TOP += STEP

        figure_data = df_data\
            [df_data.departamento_id.isin(figure_department_idx)]
        
        # Plot each deapartment's time series in its own facet
        g = seaborn.relplot(
            data=figure_data,
            x=time_col,
            y=rate_col,
            col=hue_col,
            hue=hue_col,
            kind="line",
            palette="crest",
            linewidth=4,
            zorder=5,
            col_wrap=col_wrap,
            height=2,
            aspect=1.5,
            legend=False
        )
        
        # fig size calculation:
        #
        plots_number = len(figure_data.departamento_id.unique())
        row_n = plots_number // 3
        # if integer division is ligual to floating division, cells are sufficient, skip
        if ((plots_number / 3) - row_n) > 0:
            row_n += 1
        fig_size = 15, 2.5 * row_n
        
        g.fig.set_size_inches(*fig_size)

        # Iterate over each subplot to customize further
        for departamento, ax in g.axes_dict.items():

            # Add the title as an annotation within the plot
            ax.text(
                .8, .85,
                dict_names[departamento],
                transform=ax.transAxes,
                horizontalalignment='right',
                fontweight="bold"
            )

            # Plot every year's time series in the background
            # plot the provincial context values!
            seaborn.lineplot(
                data=df_data,
                x=time_col,
                y=rate_col,
                units=time_col,
                estimator=None,
                color=".7",
                linewidth=1.5,
                ax=ax,
            )
            ax.tick_params(
                axis='x',
                rotation=45
            )

        # Reduce the frequency of the x axis ticks
        #ax.set_xticks(ax.get_xticks()[::2])

        # Tweak the supporting aspects of the plot
        g.set_titles("")
        g.set_axis_labels(
            time_col.capitalize(),
            rate_col.capitalize()
        )

        #plt.tight_layout()
        #plt.suptitle(f"Provincia: {nombres_de_provincias_por_id[province_id]}")
        if (TOTAL / STEP) <= 1:
            # si tengo una cantidad de gráficos que entra solo en un paso
            plt.suptitle(f"{figure_title}")
        else:
            plt.suptitle(f"{figure_title} - PARTE {part}")
        
        if only_save:
            plt.ioff()
            figure_name_i = figure_name.replace('.png', f'-{part}.png')
            plt.savefig(
                figure_name_i, dpi=300, bbox_inches="tight")
            plt.close()
            if verbose:
                print(f"{figure_name_i} created...")

        part += 1
        plt.show()


# + tags=[]
# get the name of the province according to a given id
#

# get unique pair combination province name - province id:
province_names_idx_df = \
    departments_shape[['provincia_id', 'provincia_nombre']]\
        .drop_duplicates()\
        .sort_values(by='provincia_nombre')\
        .reset_index(drop=True)

# create a dict name:
province_names_dict = {
    item['provincia_id']: item['provincia_nombre']
    for item
    in province_names_idx_df.to_dict(orient='records')
}

print(province_names_dict)

# + [markdown] tags=[]
# ## Prueba para una provincia

# + tags=[]
# pick only one: 26 Chubut
province_id = '14'

data_provincia_i = \
    df[df.departamento_id.str.startswith(province_id)]

# get unique pair combination department name - department id:
department_names_idx_df =\
    departments_shape\
        [departments_shape.departamento_id.str.startswith(province_id)]\
        [['departamento_id', 'departamento_nombre']]

department_names_dict = {
    elem['departamento_id']: elem['departamento_nombre']
    for elem 
    in department_names_idx_df.to_dict(orient='records')}


# + tags=[]
plot_tasas_by_departments(
    data_provincia_i,
    department_names_dict,
    time_col='periodo',
    figure_title=f"Provincia: {province_names_dict[province_id]}"
)

# + [markdown] tags=[]
# ## Bucle todas las provincias

# + [markdown] tags=[]
# Bucle por todas las provincias guardando las figuras

# + tags=[]
provinces_codes = \
    df.departamento_id.str.slice(0, 2).unique()

for province_id in provinces_codes:
    data_provincia_i = \
        df[df.departamento_id.str.startswith(province_id)]
    
    # get unique pair combination department name - department id:
    department_names_idx_df =\
        departments_shape\
            [departments_shape.departamento_id.str.startswith(province_id)]\
            [['departamento_id', 'departamento_nombre']]

    department_names_dict = {
        elem['departamento_id']: elem['departamento_nombre']
        for elem 
        in department_names_idx_df.to_dict(orient='records')}

    province_name_for_path = province_names_dict[province_id].replace(' ', '_')
    GRID_PNG_DIR = f"{TMP_FOLDER_DIR}/rates-{province_name_for_path}.png"

    plot_tasas_by_departments(
        data_provincia_i,
        department_names_dict,
        time_col='periodo',
        only_save=True,
        figure_name=GRID_PNG_DIR,
        figure_title=f"Provincia: {province_names_dict[province_id]}",
        verbose=True
    )


# + tags=[]
Image(filename='./plot-rates-quinquenios-tmp-data/rates-Mendoza-1.png')

# + tags=[] active=""
#
#
#
#
#

# + [markdown] tags=[]
# # Reporte

# + tags=[]
# HTML template to add our data and plots
report_template = '''
<!DOCTYPE html>
    <html>
        <head>
            <meta charset='utf-8'>
            <title>PDF - Tasas departamentales por quinquenio</title>
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
def get_fig_template(fig_src: str, width: int, height: int):
    return f'''
        <figure>
        <img src="{fig_src}" width="{width}" height="{height}">
        </figure>
    '''
close_tag = '''
    </html>
'''

# + tags=[]
figure_names = sorted(glob.glob(f"{TMP_FOLDER_DIR}/rates-*.png"))

report_content = report_template
# add maps:
report_content += '''
    <h2 align="center">Mapas quinquenales</h2>
'''
report_content += get_fig_template(MAPS_PNG_DIR, 1200, 450)

# add lineplots:
report_content += '''
    <div style = "display:block; clear:both; page-break-after:always;"></div>
    <h1 align="center">Tasas quinquenales por departamentos</h2>
'''

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
    report_content += get_fig_template(figure_name, FIGURE_MAX_WIDTH, height)
    print(figure_name, FIGURE_MAX_WIDTH, height)


# close
report_content += close_tag

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
HTML_REPORT_DIR = "tmp_report_quinquenios.html"
with open(HTML_REPORT_DIR, "w") as r:
    r.write(report_content)
#Use pdfkit to create the pdf report from the 
pdfkit.from_file(
    HTML_REPORT_DIR,
    str(product['data']),
    options=options
) 

# + [markdown] tags=[]
# # Eliminar datos temporales

# + tags=[]
# remove the tmp data
os.remove(HTML_REPORT_DIR)
shutil.rmtree(TMP_FOLDER_DIR)
# -


