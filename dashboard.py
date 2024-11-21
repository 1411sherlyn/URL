import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import pandas as pd

# Cargar los datos desde el archivo CSV
data = pd.read_csv("Promedios_Simples_y_Votos_Totales_por_Estado_y_A_o.csv")

# Crear la aplicación Dash
app = Dash(__name__)

# Lista de opciones únicas para los menús desplegables
opciones_anio = sorted(data["year"].unique())
opciones_estado = sorted(data["state"].unique())

# Diseño del tablero
app.layout = html.Div([
    html.H1("Elecciones Presidenciales de EE.UU.", style={'text-align': 'center'}),

    # Filtros de selección de año y estado
    html.Div([
        html.Label("Selecciona un Año:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id="selector-anio",
            options=[{"label": anio, "value": anio} for anio in opciones_anio],
            value=opciones_anio[0],
            clearable=False,
            style={'width': '45%', 'display': 'inline-block', 'margin-right': '2%'}
        ),
        html.Label("Selecciona un Estado:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id="selector-estado",
            options=[{"label": estado, "value": estado} for estado in opciones_estado],
            value=None,
            placeholder="Todos los estados",
            clearable=True,
            style={'width': '48%', 'display': 'inline-block'}
        )
    ]),

    # Mapa interactivo
    dcc.Graph(
        id="mapa-eeuu"
    ),

    # Primera fila de gráficos
    html.Div([
        dcc.Graph(
            id="grafico-tendencias",
            style={"display": "inline-block", "width": "49%"}
        ),
        dcc.Graph(
            id="comparacion-votos",
            style={"display": "inline-block", "width": "49%"}
        )
    ]),

    # Segunda fila de gráficos
    html.Div([
        dcc.Graph(
            id="grafico-total-votos-estado",
            style={"display": "inline-block", "width": "49%"}
        ),
        dcc.Graph(
            id="grafico-porcentaje-votos-partidos",
            style={"display": "inline-block", "width": "49%"}
        )
    ])
])

# Callback para actualizar los gráficos basados en las selecciones
@app.callback(
    [Output("mapa-eeuu", "figure"),
     Output("grafico-tendencias", "figure"),
     Output("comparacion-votos", "figure"),
     Output("grafico-total-votos-estado", "figure"),
     Output("grafico-porcentaje-votos-partidos", "figure")],
    [Input("selector-anio", "value"),
     Input("selector-estado", "value")]
)
def actualizar_graficos(anio_seleccionado, estado_seleccionado):
    # Filtrar los datos según el año y el estado seleccionados
    datos_filtrados = data[data["year"] == anio_seleccionado]
    if estado_seleccionado:
        datos_filtrados = datos_filtrados[datos_filtrados["state"] == estado_seleccionado]

    # Mapa interactivo
    mapa_figura = px.choropleth(
        datos_filtrados,
        locations="state",
        locationmode="USA-states",
        color="d_percent_avg",
        hover_name="state",
        hover_data=["year", "total_votes_sum", "d_percent_avg", "r_percent_avg", "other_percent_avg"],
        scope="usa",
        title=f"Porcentaje de votos demócratas por Estado en {anio_seleccionado}",
        color_continuous_scale=px.colors.sequential.Blues
    )

    # Gráfico de tendencias (ahora de barras)
    if not datos_filtrados.empty:
        datos_tendencias = data[data["state"] == estado_seleccionado] if estado_seleccionado else data
        figura_tendencias = px.bar(
            datos_tendencias,
            x="year",
            y=["d_percent_avg", "r_percent_avg", "other_percent_avg"],
            barmode="group",
            labels={"value": "Porcentaje de Votos", "year": "Año", "variable": "Partido"},
            title="Porcentaje de Votos por Partido",
            color_discrete_map={
                "d_percent_avg": "blue",
                "r_percent_avg": "green",
                "other_percent_avg": "red"
            },
            template="plotly"
        )
    else:
        figura_tendencias = px.bar(title="Porcentaje de Votos por Partido (Sin Datos)", template="plotly")

    # Gráfico de comparación de votos totales por estado
    figura_comparacion = px.bar(
        datos_filtrados,
        x="state",
        y="total_votes_sum",
        color="state",
        title="Comparación de Votos Totales por Estado",
        labels={"total_votes_sum": "Votos Totales", "state": "Estado"},
        color_continuous_scale=px.colors.sequential.Plasma
    )

    # Gráfico de total de votos por estado (coloreado según partido ganador)
    if not datos_filtrados.empty:
        datos_filtrados["Ganador"] = datos_filtrados.apply(
            lambda row: "Demócrata" if row["d_percent_avg"] > row["r_percent_avg"] and row["d_percent_avg"] > row["other_percent_avg"] else
                        "Republicano" if row["r_percent_avg"] > row["d_percent_avg"] and row["r_percent_avg"] > row["other_percent_avg"] else
                        "Otros",
            axis=1
        )

        figura_total_votos_estado = px.bar(
            datos_filtrados,
            x="state",
            y="total_votes_sum",
            color="Ganador",
            color_discrete_map={
                "Demócrata": "blue",
                "Republicano": "green",
                "Otros": "red"
            },
            title="Total de Votos por Estado",
            labels={"total_votes_sum": "Votos Totales", "state": "Estado"},
            text="total_votes_sum",
            template="plotly"
        )
    else:
        figura_total_votos_estado = px.bar(
            title="Total de Votos por Estado ",
            template="plotly"
        )

    # Nuevo gráfico: Porcentaje de votos por partido
    if not datos_filtrados.empty:
        promedio_democrata = datos_filtrados["d_percent_avg"].mean()
        promedio_republicano = datos_filtrados["r_percent_avg"].mean()
        promedio_otros = datos_filtrados["other_percent_avg"].mean()
        datos_partidos = pd.DataFrame({
            "Partido": ["Demócrata", "Republicano", "Otros"],
            "Porcentaje": [promedio_democrata, promedio_republicano, promedio_otros],
            "Color": ["blue", "green", "red"]
        })

        figura_porcentaje_votos_partidos = px.bar(
            datos_partidos,
            x="Partido",
            y="Porcentaje",
            color="Partido",
            text="Porcentaje",
            color_discrete_map={
                "Demócrata": "blue",
                "Republicano": "green",
                "Otros": "red"
            },
            title="Porcentaje de Votos por Partido",
            labels={"Porcentaje": "Porcentaje de Votos", "Partido": "Partido"},
            template="plotly"
        )
    else:
        figura_porcentaje_votos_partidos = px.bar(
            title="Porcentaje de Votos por Partido",
            template="plotly"
        )

    return (mapa_figura, figura_tendencias, figura_comparacion, figura_total_votos_estado, figura_porcentaje_votos_partidos)

# Ejecutar el servidor
if __name__ == '__main__':
    app.run_server(debug=True)
