import pandas as pd
import plotly.express as px
import os
import dash
from dash import html, Input, Output, dcc
 
#Cargar los datos
ruta = os.path.join(os.path.dirname(__file__), 'notas_limpio.xlsx')
dataf = pd.read_excel(ruta)
print(dataf)
 
#Iniciar app
appnotas = dash.Dash(__name__)
#Crear el layout
appnotas.layout = html.Div([
                    html.H1("Tablero de notas estudiantes", style={"textAlign": "center",
                                                    'color': '#333',
                                                    "padding": "20px",
                                                    "fontFamily": "cursive",
                                                    "backgroundColor": "#8fcfb7"}),
                    html.Label("Seleccionar Materia: ", style={"margin": "10px"}),
                    dcc.Dropdown(id="filtro_materia",
                                 options=[{"label":Carrera,"value":Carrera} for Carrera in sorted(dataf["Carrera"].unique())],
                                 value=dataf["Carrera"].unique()[0],
                                 style={"width": "200px", "margin": "auto"}
                                 ),
                    html.Br(),
 
                    #Crear los tabs de los graficos
                    dcc.Tabs([
                        dcc.Tab(label="Grafico de promedio", children=[dcc.Graph(id="histograma")]),
                    ],style={"fontWeight": "bold", "color": "#333", "backgroundColor": "#2c3e50"}),
 
                    dcc.Tab(label="Edad vs promedios", children=[dcc.Graph(id="dispersion")]),
                    dcc.Tab(label="Desempeño", children=[dcc.Graph(id="pie")]),
                    dcc.Tab(label="Promedio notas x carrera", children=[dcc.Graph(id="barras")])
])
 
#Actualizar el grafico
@appnotas.callback(
    Output("histograma", "figure"),
    Output("dispersion", "figure"),
    Output("pie", "figure"),
    Output("barras", "figure"),
    Input("filtro_materia", "value")
)
 
#funcion para crear el grafico
def actualizarG(filtro_materia):
    filtro = dataf[dataf["Carrera"]==filtro_materia]
 
    #Crear los graficos
    histo = px.histogram(filtro, x ="Promedio", nbins=10, title=f"Distribución de Promedios - {filtro_materia}",
                         color_discrete_sequence=["#9be011"]).update_layout(template="plotly_white", yaxis_title="Cantidad de estudiantes")
    disper = px.scatter(filtro, x="Edad", y="Promedio", color="Desempeño", title=f"Edad vs Promedio - {filtro_materia}",
                        color_discrete_sequence=px.colors.qualitative.Set2).update_layout(template="plotly_white")
    pie = px.pie(filtro, names="Desempeño",title=f"Desempeño - {filtro_materia}")
    promedios = filtro.groupby("Carrera")["Promedio"].mean().reset_index()
 
    barras = px.bar(promedios, x="Carrera", y="Promedio", title=f"Promedio de notas por Carrera", color="Carrera",
                     color_discrete_sequence=px.colors.qualitative.Set3).update_layout(template="plotly_white")
    return histo, disper, pie, barras
#Ejecutar la app
if __name__ == '__main__':
    appnotas.run(debug=True)