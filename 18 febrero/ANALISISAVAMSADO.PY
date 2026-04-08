import pandas as pd
import plotly.express as px
import os
import dash
from dash import html, Input, Output, dcc
from dash import dash_table
 
#Cargar los Datos.
ruta = os.path.join(os.path.dirname(__file__), 'notas_limpio.xlsx')
dataf = pd.read_excel(ruta)
 
#Iniciar App.
appnotas = dash.Dash(__name__)
 
appnotas.layout = html.Div([
 
    html.H1(
        "Tablero Avanzado",
        style={
            "textAlign": "center",
            "backgroundColor": "#353968",
            "color": "#333",
            "padding": "20px",
            "fontFamily": "cursive"
        }
    ),
 
    #Crear filtros.
    html.Div([
 
        html.Label("Seleccionar Carrera"),
 
        dcc.Dropdown(
            id="filtro_carrera",
            options=[{"label": ca, "value": ca}
                     for ca in sorted(dataf["Carrera"].unique())],
            value=dataf["Carrera"].unique()[0],
        ),
 
        html.Br(),
 
        html.Label("Rango de edad"),
 
        dcc.RangeSlider(
            id="slider_edad",
            min=dataf["Edad"].min(),
            max=dataf["Edad"].max(),
            step=1,
            value=[dataf["Edad"].min(), dataf["Edad"].max()],
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        html.Br(),
        html.Label("Rango de promedio"),
        dcc.RangeSlider(
            id="slider_promedio",
            min=0,
            max=5,
            step=1.5,
            value=[0, 5],
            tooltip={"placement": "bottom", "always_visible": True}
        ),
       
 
 
    ],style={"width":"80%","margin":"auto"}),
    html.Br(),

    #Crear los kips.
    html.Div(id="kips",
             style={"display":"flex",
                    "justifyContent":"space-around",
                    "backgroundColor":"#f0f0f0",
                    "padding":"20px",
                    "borderRadius":"10px"}),
                    html.Br(),
                   
        #Crear una Tabla.
        dcc.Loading(dash_table.DataTable(id="tabla",
                                         page_size = 8,
                                         filter_action="native",
                                         sort_action="native",
                                         row_selectable="multi",
                                         selected_rows=[],
                                         style_table={"overflowX": "auto"},
                                         style_cell={"textAlign": "center", "padding": "5px"}
                                         ),
                                         type="circle"
                                         ),
                                         html.Br(),
                                         
    #Crear los graficos interactivos
    dcc.Loading(
        dcc.Graph(id="gra_detallado"),
        type="default"
    ),
    html.Br(),

    #Crear los tabs.

    dcc.Tabs([
        dcc.Tab(label="Histograma", children=[dcc.Graph(id="histograma")]),
        dcc.Tab(label="Dispersion", children=[dcc.Graph(id="dispersion")]),
        dcc.Tab(label="Desempeño", children=[dcc.Graph(id="Pie")]),
    ])
   
])
 
#Actualización de la tabla y gráfico general.

@appnotas.callback(
    Output("tabla", "data"),
    Output("tabla", "columns"),
    Output("kips", "children"),
    Input("filtro_carrera", "value"),
    Input("slider_edad", "value"),
    Input("slider_promedio", "value")
    
    )

def actualizartab (rows, selected_rows):
    if rows is None:
        return px.scatter(title = "Sin Datos")

    dff = pd.dataf(rows)

    if selected_rows:
        dff = dff.iloc[selected_rows]

        fig = px.scatter(dff, x="Edad", y="Promedio", color ="Carrera",
                         title="Análisis Detallado (Seleccione las filas para ver el detalle)",
                         trendline = "ols"
                         )
        



def actualizar_comp(carrera, rangoedad,rangoprome):
   
    filtro=dataf[
        (dataf["Carrera"]==carrera) &
        (dataf["Edad"]>=rangoedad[0]) &
        (dataf["Edad"]<=rangoedad[1]) &
        (dataf["Promedio"]>=rangoprome[0]) &
        (dataf["Promedio"]<=rangoprome[1])
       
    ]
 
   
    #Creación de Kips.
    promedio=round(filtro["Promedio"].mean(),2)
    total=len(filtro)
    maximo=round(filtro["Promedio"].mean(),2)
   
    kips = [
        html.Div([html.H4("Promedio"), html.H2(promedio,)],
                 style={"backgroundColor": "#e0f7fa",
                        "padding": "10px",
                        "borderRadius": "5px",
                        "width": "30%"}),
       
        html.Div([html.H4("Total estudiantes"), html.H2(total,)],
                 style={"backgroundColor": "#e0f7fa",
                        "padding": "10px",
                        "borderRadius": "5px",
                        "width": "30%"}),
       
        html.Div([html.H4("Maximo"), html.H2(maximo,)],
                 style={"backgroundColor": "#e0f7fa",
                        "padding": "10px",
                        "borderRadius": "5px",
                        "width": "30%"}),
    ]
   
    return(filtro.to_dict("records"),
           [{"name":i,"id":i} for i in filtro.columns],
           kips)

 
#Ejecutar App.
if __name__ == '__main__':
    appnotas.run(debug=True)