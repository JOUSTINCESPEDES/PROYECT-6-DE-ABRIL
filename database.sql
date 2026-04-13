import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, Input, Output, dash_table
from database import obtener_estudiantes


# ─────────────────────────────────────────────────────────────
# CONSTANTES DE COLOR  (usadas sólo para los gráficos Plotly)
# El CSS del layout vive en assets/style.css
# ─────────────────────────────────────────────────────────────
C = {
    'bg':      '#0a0c10',
    'surface': '#111318',
    'border':  'rgba(255,255,255,0.07)',
    'accent':  '#6c63ff',
    'accent2': '#00d4aa',
    'danger':  '#ff6b6b',
    'gold':    '#f5c842',
    'text':    '#e8eaf0',
    'muted':   '#6b7280',
}

# Tema base para todas las figuras Plotly
PLOTLY_LAYOUT = dict(
    paper_bgcolor = 'rgba(0,0,0,0)',
    plot_bgcolor  = 'rgba(0,0,0,0)',
    font          = dict(family='DM Sans, sans-serif', color=C['text'], size=13),
    title         = dict(font=dict(family='Syne, sans-serif', size=17, color=C['text']), x=0.02),
    xaxis         = dict(gridcolor='rgba(255,255,255,0.05)', linecolor='rgba(255,255,255,0.08)',
                         tickcolor=C['muted'], tickfont=dict(color=C['muted']), zeroline=False),
    yaxis         = dict(gridcolor='rgba(255,255,255,0.05)', linecolor='rgba(255,255,255,0.08)',
                         tickcolor=C['muted'], tickfont=dict(color=C['muted']), zeroline=False),
    colorway      = [C['accent'], C['accent2'], C['gold'], C['danger'], '#f472b6', '#34d399'],
    legend        = dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(255,255,255,0.08)',
                         font=dict(color=C['muted'], size=12)),
    margin        = dict(l=50, r=20, t=52, b=40),
)


def _theme(fig):
    """Aplica el tema oscuro a una figura Plotly."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ─────────────────────────────────────────────────────────────
# LAYOUT  —  sólo clases CSS, sin estilos inline
# ─────────────────────────────────────────────────────────────
def _layout(dataf):
    return html.Div(className='dash-root', children=[

        # ── Cabecera ──────────────────────────────────────────
        html.Div(className='dash-header', children=[
            html.Div(className='dash-header__brand', children=[
                html.Div('📊', className='brand-icon brand-icon--lg'),
                html.Div([
                    html.H1('Tablero Avanzado', className='dash-header__title'),
                    html.P('Análisis de desempeño estudiantil en tiempo real',
                           className='dash-header__subtitle'),
                ]),
            ]),
        ]),

        # ── Filtros ───────────────────────────────────────────
        html.Div(className='dash-filters', children=[

            html.Div([
                html.Label('Carrera', className='filter-label'),
                dcc.Dropdown(
                    id='filtro_carrera',
                    options=[{'label': c, 'value': c} for c in sorted(dataf['carrera'].unique())],
                    value=dataf['carrera'].unique()[0],
                ),
            ]),

            html.Div([
                html.Label('Rango de edad', className='filter-label'),
                dcc.RangeSlider(
                    id='slider_edad',
                    min=dataf['edadEstu'].min(), max=dataf['edadEstu'].max(), step=1,
                    value=[dataf['edadEstu'].min(), dataf['edadEstu'].max()],
                    tooltip={'placement': 'bottom', 'always_visible': True},
                ),
            ]),

            html.Div([
                html.Label('Rango de promedio', className='filter-label'),
                dcc.RangeSlider(
                    id='slider_promedio',
                    min=0, max=5, step=0.5, value=[0, 5],
                    tooltip={'placement': 'bottom', 'always_visible': True},
                ),
            ]),

        ]),

        # ── KPIs ──────────────────────────────────────────────
        html.Div(id='kpis', className='dash-kpis'),

        # ── Búsqueda ──────────────────────────────────────────
        html.Div(className='dash-search-wrap', children=[
            dcc.Input(id='busqueda', type='text',
                      placeholder='🔍  Buscar estudiante...',
                      className='dash-search'),
        ]),

        # ── Tabla ─────────────────────────────────────────────
        html.Div(className='dash-table-wrap', children=[
            dcc.Loading(
                dash_table.DataTable(
                    id='tabla',
                    page_size=8,
                    filter_action='native',
                    sort_action='native',
                    row_selectable='multi',
                    selected_rows=[],
                    style_table={
                        'overflowX': 'auto',
                        'borderRadius': '14px',
                        'border': f'1px solid {C["border"]}',
                        'overflow': 'hidden',
                    },
                    style_header={
                        'backgroundColor': C['surface'],
                        'color': C['muted'],
                        'fontWeight': '500',
                        'fontSize': '11px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.8px',
                        'border': 'none',
                        'borderBottom': f'1px solid {C["border"]}',
                        'padding': '12px 16px',
                    },
                    style_data={
                        'backgroundColor': C['bg'],
                        'color': C['text'],
                        'border': 'none',
                        'borderBottom': 'none',
                        'fontSize': '13px',
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'},
                         'backgroundColor': 'rgba(255,255,255,0.015)'},
                        {'if': {'state': 'selected'},
                         'backgroundColor': 'rgba(108,99,255,0.12)',
                         'border': '1px solid rgba(108,99,255,0.3)'},
                    ],
                    style_cell={'textAlign': 'center', 'padding': '11px 16px'},
                    style_filter={
                        'backgroundColor': C['surface'],
                        'color': C['text'],
                        'border': 'none',
                        'borderBottom': f'1px solid {C["border"]}',
                    },
                ),
                type='circle', color=C['accent'],
            ),
        ]),

        dcc.Interval(id='intervalo', interval=10000, n_intervals=0),

        # ── Gráfico detallado ─────────────────────────────────
        html.Div(className='dash-chart-wrap', children=[
            dcc.Loading(
                dcc.Graph(id='gra_detallado', config={'displayModeBar': False}),
                type='default', color=C['accent'],
            ),
        ]),

        # ── Tabs ──────────────────────────────────────────────
        html.Div(className='dash-tabs-wrap', children=[
            dcc.Tabs(
                colors={'border': C['border'], 'primary': C['accent'], 'background': C['surface']},
                children=[
                    dcc.Tab(label='Histograma', children=[
                        html.Div(className='dash-tab-content',
                                 children=[dcc.Graph(id='histograma', config={'displayModeBar': False})])
                    ]),
                    dcc.Tab(label='Dispersión', children=[
                        html.Div(className='dash-tab-content',
                                 children=[dcc.Graph(id='dispersion', config={'displayModeBar': False})])
                    ]),
                    dcc.Tab(label='Desempeño', children=[
                        html.Div(className='dash-tab-content',
                                 children=[dcc.Graph(id='pie', config={'displayModeBar': False})])
                    ]),
                ],
            ),
        ]),

    ])


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────
def crear_tablero(server):

    dataf = obtener_estudiantes()
    dataf.columns = dataf.columns.str.strip()

    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_principal/',
        suppress_callback_exceptions=True,
        # Dash carga automáticamente todo lo que esté en /assets
        assets_folder='assets',
        external_stylesheets=[
            'https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap'
        ],
    )

    app.layout = _layout(dataf)

    # ── Callback principal ────────────────────────────────────
    @app.callback(
        Output('tabla',      'data'),
        Output('tabla',      'columns'),
        Output('kpis',       'children'),
        Output('histograma', 'figure'),
        Output('dispersion', 'figure'),
        Output('pie',        'figure'),

        Input('filtro_carrera',  'value'),
        Input('slider_edad',     'value'),
        Input('slider_promedio', 'value'),
        Input('busqueda',        'value'),
        Input('intervalo',       'n_intervals'),
    )
    def actualizar_comp(carrera, rango_edad, rango_promedio, busqueda, intervalo):
        dataf = obtener_estudiantes()

        filtro = dataf[
            (dataf['carrera']  == carrera) &
            (dataf['edadEstu'] >= rango_edad[0]) &
            (dataf['edadEstu'] <= rango_edad[1]) &
            (dataf['promedio'] >= rango_promedio[0]) &
            (dataf['promedio'] <= rango_promedio[1])
        ].copy()

        if busqueda:
            filtro = filtro[filtro['nombreEstu'].str.contains(busqueda, case=False, na=False)]
            filtro = filtro[filtro.apply(lambda row: busqueda.lower() in str(row).lower(), axis=1)]

        # KPIs
        promedio = round(filtro['promedio'].mean(), 2) if len(filtro) > 0 else 0
        total    = len(filtro)
        maximo   = round(filtro['promedio'].max(), 2)  if len(filtro) > 0 else 0

        kpi_items = [
            ('📈', 'Promedio',          promedio, 'kpi-card kpi-card--accent'),
            ('👥', 'Total estudiantes', total,    'kpi-card kpi-card--accent2'),
            ('🏆', 'Nota máxima',       maximo,   'kpi-card kpi-card--gold'),
        ]
        kpis = [
            html.Div(className=cls, children=[
                html.Div(icon, className='kpi-icon'),
                html.Div([
                    html.P(label, className='kpi-label'),
                    html.H2(str(value), className='kpi-value'),
                ]),
            ])
            for icon, label, value, cls in kpi_items
        ]

        # Histograma
        fig_hist = px.histogram(filtro, x='promedio', nbins=10,
                                title='Distribución de Promedios',
                                color_discrete_sequence=[C['accent']])
        fig_hist.update_traces(marker_line_color='rgba(255,255,255,0.1)',
                               marker_line_width=1, opacity=0.85)
        _theme(fig_hist)

        # Dispersión
        fig_disp = px.scatter(filtro, x='promedio', y='edadEstu',
                              color='promedio', size='promedio',
                              title='Dispersión: Promedio vs Edad',
                              color_continuous_scale=[[0, C['danger']], [0.5, C['accent']], [1, C['accent2']]])
        fig_disp.update_traces(marker_line_color='rgba(255,255,255,0.1)', marker_line_width=1)
        _theme(fig_disp)

        # Pie (donut)
        edad_prom = filtro.groupby('edadEstu')['promedio'].mean().reset_index()
        fig_pie = px.pie(edad_prom, values='promedio', names='edadEstu',
                         title='Promedio por Edad', hole=0.4,
                         color_discrete_sequence=[C['accent'], C['accent2'], C['gold'],
                                                  C['danger'], '#f472b6', '#34d399', '#fb923c'])
        fig_pie.update_traces(textfont_color=C['text'],
                              marker_line_color=C['surface'], marker_line_width=2)
        _theme(fig_pie)

        return (
            filtro.to_dict('records'),
            [{'name': i, 'id': i} for i in filtro.columns],
            kpis,
            fig_hist,
            fig_disp,
            fig_pie,
        )

    # ── Gráfico detallado ─────────────────────────────────────
    @app.callback(
        Output('gra_detallado', 'figure'),
        Input('tabla', 'derived_virtual_data'),
        Input('tabla', 'derived_virtual_selected_rows'),
    )
    def actualizar_tabla(rows, selected_rows):
        if rows is None:
            return _theme(px.scatter(title='Sin datos seleccionados'))

        dff = pd.DataFrame(rows)
        if selected_rows:
            dff = dff.iloc[selected_rows]

        fig = px.scatter(dff, x='edadEstu', y='promedio',
                         size='promedio', color='carrera',
                         title='Análisis detallado (selección de tabla)',
                         trendline='ols')
        fig.update_traces(marker_line_color='rgba(255,255,255,0.1)', marker_line_width=1)
        return _theme(fig)

    return app
