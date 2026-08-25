from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st


# ============================================================
# RADAR DE TURISMO DE NATURALEZA Y AVENTURA DEL PERÚ
# IRNA-C 2026
# MVP DASHBOARD - V2.1
#
# Incluye:
# - KPIs nacionales
# - Mapa territorial IRNA-C
# - Top 15 nacional
# - Ficha territorial
# - Radar de 5 dimensiones
# - Barras por dimensión
# - Lectura estratégica automática
# - Sensibilidad del ranking
# - Comparador entre territorios
# - Ranking nacional completo
# - Nota metodológica
# ============================================================


# ============================================================
# CONFIGURACIÓN STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Radar Turismo Naturaleza y Aventura - Perú",
    page_icon="🧭",
    layout="wide"
)


# ============================================================
# ARCHIVOS
# ============================================================

ARCHIVO = Path(
    "outputs/radar_fase2_irnac_modelo_base_2026.xlsx"
)

GEOJSON_URL = (
    "https://raw.githubusercontent.com/"
    "juaneladio/peru-geojson/master/"
    "peru_departamental_simple.geojson"
)


# ============================================================
# ESTILO GENERAL
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1 {
        color: #173f35;
        font-weight: 750;
    }

    h2 {
        color: #173f35;
        font-weight: 700;
    }

    h3 {
        color: #245b4c;
    }

    div[data-testid="stMetric"] {
        background-color: #f7f9f8;
        border: 1px solid #e0e7e3;
        border-radius: 12px;
        padding: 14px;
    }

    div[data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    .radar-box {
        background-color: #f7f9f8;
        border: 1px solid #e0e7e3;
        border-radius: 12px;
        padding: 18px;
    }

    .lectura-box {
        background-color: #f4f7f6;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #2e7d65;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .small-note {
        color: #6d7471;
        font-size: 0.9rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data
def cargar_datos():

    if not ARCHIVO.exists():

        raise FileNotFoundError(
            f"No se encontró:\n{ARCHIVO}"
        )

    ranking = pd.read_excel(
        ARCHIVO,
        sheet_name="02_Ranking_IRNAC"
    )

    sensibilidad = pd.read_excel(
        ARCHIVO,
        sheet_name="07_Sensibilidad"
    )

    escenarios = pd.read_excel(
        ARCHIVO,
        sheet_name="05_Escenarios_Scores"
    )

    pesos = pd.read_excel(
        ARCHIVO,
        sheet_name="09_Pesos_Escenarios"
    )

    return (
        ranking,
        sensibilidad,
        escenarios,
        pesos
    )


@st.cache_data
def cargar_geojson():

    try:

        respuesta = requests.get(
            GEOJSON_URL,
            timeout=30
        )

        if respuesta.status_code == 200:

            return respuesta.json()

    except Exception:

        pass

    return None


ranking, sensibilidad, escenarios, pesos = cargar_datos()

geojson = cargar_geojson()


# ============================================================
# HOMOLOGACIÓN MAPA
# ============================================================

MAPA_EQUIVALENCIAS = {

    "PROVINCIA CONSTITUCIONAL DEL CALLAO":
        "CALLAO",

    "ANCASH":
        "ANCASH",

    "APURIMAC":
        "APURIMAC",

    "HUANUCO":
        "HUANUCO",

    "JUNIN":
        "JUNIN",

    "SAN MARTIN":
        "SAN MARTIN"
}


ranking[
    "Departamento_Mapa"
] = (
    ranking[
        "Departamento"
    ]
    .replace(
        MAPA_EQUIVALENCIAS
    )
)


# ============================================================
# CABECERA
# ============================================================

st.title(
    "🧭 Radar de Turismo de Naturaleza y Aventura del Perú"
)

st.subheader(
    "IRNA-C 2026 | Índice de Competitividad Territorial"
)

st.caption(
    "MVP experimental · "
    "25 territorios · "
    "15 indicadores · "
    "5 dimensiones"
)

st.info(
    "El IRNA-C 2026 es un modelo experimental. "
    "Los resultados deben interpretarse como una herramienta "
    "de análisis territorial y no como un índice oficial."
)


# ============================================================
# KPIs NACIONALES
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        "Territorios",
        len(ranking)
    )

with c2:

    st.metric(
        "IRNA-C máximo",
        f"{ranking['IRNA_C'].max():.1f}"
    )

with c3:

    st.metric(
        "IRNA-C mediana",
        f"{ranking['IRNA_C'].median():.1f}"
    )

with c4:

    robustos = int(
        sensibilidad[
            "Robustez_Ranking"
        ]
        .isin(
            [
                "MUY ROBUSTO",
                "ROBUSTO"
            ]
        )
        .sum()
    )

    st.metric(
        "Territorios robustos",
        robustos
    )

with c5:

    lider = (
        ranking
        .sort_values(
            "IRNA_C",
            ascending=False
        )
        .iloc[0][
            "Departamento"
        ]
    )

    st.metric(
        "Líder nacional",
        lider
    )


st.divider()


# ============================================================
# PANORAMA NACIONAL
# ============================================================

st.header(
    "Panorama nacional"
)


col_mapa, col_rank = st.columns(
    [1.15, 1]
)


# ============================================================
# MAPA
# ============================================================

with col_mapa:

    st.subheader(
        "Mapa territorial IRNA-C"
    )

    if geojson is not None:

        fig_mapa = px.choropleth(
            ranking,
            geojson=geojson,
            locations="Departamento_Mapa",
            featureidkey="properties.NOMBDEP",
            color="IRNA_C",
            hover_name="Departamento",
            hover_data={
                "Ranking_IRNA_C": True,
                "Categoria_IRNA_C": True,
                "IRNA_C": ":.1f",
                "Departamento_Mapa": False
            },
            color_continuous_scale="YlGn",
            range_color=[
                0,
                100
            ]
        )

        fig_mapa.update_geos(
            fitbounds="locations",
            visible=False,
            projection_type="mercator"
        )

        fig_mapa.update_layout(
            height=650,
            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),
            coloraxis_colorbar=dict(
                title="IRNA-C",
                thickness=15,
                len=0.65,
                x=0.95
            )
        )

        st.plotly_chart(
            fig_mapa,
            use_container_width=True
        )

    else:

        st.warning(
            "No se pudo cargar el mapa base. "
            "El resto del Radar continúa funcionando."
        )


# ============================================================
# TOP 15
# ============================================================

with col_rank:

    st.subheader(
        "Top 15 nacional"
    )

    top15 = (
        ranking
        .sort_values(
            "IRNA_C",
            ascending=False
        )
        .head(15)
        .sort_values(
            "IRNA_C",
            ascending=True
        )
    )

    fig_top = px.bar(
        top15,
        x="IRNA_C",
        y="Departamento",
        orientation="h",
        text="IRNA_C",
        hover_data=[
            "Ranking_IRNA_C",
            "Categoria_IRNA_C"
        ]
    )

    fig_top.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_top.update_layout(
        height=650,
        xaxis_title="IRNA-C",
        yaxis_title="",
        showlegend=False,
        margin=dict(
            l=0,
            r=40,
            t=0,
            b=0
        )
    )

    st.plotly_chart(
        fig_top,
        use_container_width=True
    )


st.divider()


# ============================================================
# FICHA TERRITORIAL
# ============================================================

st.header(
    "Ficha territorial"
)

lista_departamentos = (
    ranking[
        "Departamento"
    ]
    .tolist()
)

departamento = st.selectbox(
    "Selecciona un territorio",
    lista_departamentos
)


fila = (
    ranking[
        ranking[
            "Departamento"
        ]
        == departamento
    ]
    .iloc[0]
)


sens = (
    sensibilidad[
        sensibilidad[
            "Departamento"
        ]
        == departamento
    ]
    .iloc[0]
)


# ============================================================
# KPIs TERRITORIALES
# ============================================================

t1, t2, t3, t4, t5 = st.columns(5)

with t1:

    st.metric(
        "Ranking nacional",
        f"#{int(fila['Ranking_IRNA_C'])}"
    )

with t2:

    st.metric(
        "IRNA-C",
        f"{fila['IRNA_C']:.1f}"
    )

with t3:

    st.metric(
        "Categoría",
        fila[
            "Categoria_IRNA_C"
        ]
    )

with t4:

    st.metric(
        "Robustez",
        sens[
            "Robustez_Ranking"
        ]
    )

with t5:

    st.metric(
        "Rango ranking",
        int(
            sens[
                "Rango_Ranking"
            ]
        )
    )


# ============================================================
# DIMENSIONES TERRITORIALES
# ============================================================

dimensiones = {

    "Demanda":
        fila[
            "Score_DEMANDA"
        ],

    "Desempeño turístico":
        fila[
            "Score_DESEMPENO_TURISTICO"
        ],

    "Conectividad":
        fila[
            "Score_CONECTIVIDAD"
        ],

    "Oferta formal":
        fila[
            "Score_OFERTA_FORMAL"
        ],

    "Capital natural":
        fila[
            "Score_CAPITAL_NATURAL"
        ]
}


col_radar, col_dimensiones = st.columns(2)


# ============================================================
# RADAR
# ============================================================

with col_radar:

    st.subheader(
        "Perfil competitivo"
    )

    categorias_radar = list(
        dimensiones.keys()
    )

    valores_radar = list(
        dimensiones.values()
    )

    categorias_cerradas = (
        categorias_radar
        +
        [
            categorias_radar[0]
        ]
    )

    valores_cerrados = (
        valores_radar
        +
        [
            valores_radar[0]
        ]
    )

    fig_radar = go.Figure()

    fig_radar.add_trace(
        go.Scatterpolar(
            r=valores_cerrados,
            theta=categorias_cerradas,
            fill="toself",
            name=departamento
        )
    )

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[
                    0,
                    100
                ]
            )
        ),
        showlegend=False,
        height=500,
        margin=dict(
            l=30,
            r=30,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig_radar,
        use_container_width=True
    )


# ============================================================
# BARRAS DIMENSIONALES
# ============================================================

with col_dimensiones:

    st.subheader(
        "Scores por dimensión"
    )

    tabla_dimensiones = pd.DataFrame(
        {
            "Dimensión":
                list(
                    dimensiones.keys()
                ),

            "Score":
                list(
                    dimensiones.values()
                )
        }
    )

    tabla_dimensiones = (
        tabla_dimensiones
        .sort_values(
            "Score",
            ascending=True
        )
    )

    fig_dimensiones = px.bar(
        tabla_dimensiones,
        x="Score",
        y="Dimensión",
        orientation="h",
        text="Score"
    )

    fig_dimensiones.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_dimensiones.update_layout(
        height=500,
        xaxis=dict(
            range=[
                0,
                105
            ]
        ),
        xaxis_title="Score 0–100",
        yaxis_title="",
        showlegend=False
    )

    st.plotly_chart(
        fig_dimensiones,
        use_container_width=True
    )


# ============================================================
# LECTURA ESTRATÉGICA
# ============================================================

dimension_fuerte = max(
    dimensiones,
    key=dimensiones.get
)

dimension_debil = min(
    dimensiones,
    key=dimensiones.get
)


st.subheader(
    "Lectura estratégica"
)


st.markdown(
    f"""
    <div class="lectura-box">

    <b>{departamento}</b> ocupa el puesto
    <b>#{int(fila['Ranking_IRNA_C'])}</b>
    del ranking nacional con un IRNA-C de
    <b>{fila['IRNA_C']:.1f}</b>.

    <br><br>

    <b>Principal fortaleza:</b>
    {dimension_fuerte}
    ({dimensiones[dimension_fuerte]:.1f} puntos).

    <br><br>

    <b>Principal brecha:</b>
    {dimension_debil}
    ({dimensiones[dimension_debil]:.1f} puntos).

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INTERPRETACIÓN AUTOMÁTICA
# ============================================================

if (
    dimensiones[
        dimension_fuerte
    ]
    >= 70
    and
    dimensiones[
        dimension_debil
    ]
    < 35
):

    st.write(
        f"El territorio muestra una **brecha estructural importante**: "
        f"su fortaleza en **{dimension_fuerte}** todavía no se refleja "
        f"con la misma intensidad en **{dimension_debil}**."
    )

elif (
    max(
        dimensiones.values()
    )
    -
    min(
        dimensiones.values()
    )
    <= 20
):

    st.write(
        "El territorio presenta un perfil relativamente equilibrado "
        "entre las cinco dimensiones de competitividad."
    )

else:

    st.write(
        f"El principal reto territorial es convertir la fortaleza en "
        f"**{dimension_fuerte}** en mejores resultados en "
        f"**{dimension_debil}**."
    )


# ============================================================
# SENSIBILIDAD
# ============================================================

st.subheader(
    "Estabilidad del resultado"
)

s1, s2, s3, s4 = st.columns(4)

with s1:

    st.metric(
        "Ranking base",
        int(
            sens[
                "Ranking_Base"
            ]
        )
    )

with s2:

    st.metric(
        "Mejor posición",
        int(
            sens[
                "Ranking_Mejor"
            ]
        )
    )

with s3:

    st.metric(
        "Peor posición",
        int(
            sens[
                "Ranking_Peor"
            ]
        )
    )

with s4:

    st.metric(
        "Robustez",
        sens[
            "Robustez_Ranking"
        ]
    )


st.divider()


# ============================================================
# COMPARADOR TERRITORIAL
# ============================================================

st.header(
    "Comparador territorial"
)


comparador_1, comparador_2 = st.columns(2)


with comparador_1:

    territorio_a = st.selectbox(
        "Territorio A",
        lista_departamentos,
        index=0,
        key="territorio_a"
    )


with comparador_2:

    indice_b = (
        1
        if len(
            lista_departamentos
        )
        > 1
        else 0
    )

    territorio_b = st.selectbox(
        "Territorio B",
        lista_departamentos,
        index=indice_b,
        key="territorio_b"
    )


fila_a = (
    ranking[
        ranking[
            "Departamento"
        ]
        == territorio_a
    ]
    .iloc[0]
)


fila_b = (
    ranking[
        ranking[
            "Departamento"
        ]
        == territorio_b
    ]
    .iloc[0]
)


comparacion = pd.DataFrame(
    {
        "Dimensión": [
            "Demanda",
            "Desempeño turístico",
            "Conectividad",
            "Oferta formal",
            "Capital natural"
        ],

        territorio_a: [
            fila_a[
                "Score_DEMANDA"
            ],

            fila_a[
                "Score_DESEMPENO_TURISTICO"
            ],

            fila_a[
                "Score_CONECTIVIDAD"
            ],

            fila_a[
                "Score_OFERTA_FORMAL"
            ],

            fila_a[
                "Score_CAPITAL_NATURAL"
            ]
        ],

        territorio_b: [
            fila_b[
                "Score_DEMANDA"
            ],

            fila_b[
                "Score_DESEMPENO_TURISTICO"
            ],

            fila_b[
                "Score_CONECTIVIDAD"
            ],

            fila_b[
                "Score_OFERTA_FORMAL"
            ],

            fila_b[
                "Score_CAPITAL_NATURAL"
            ]
        ]
    }
)


fig_comparacion = go.Figure()


fig_comparacion.add_trace(
    go.Bar(
        name=territorio_a,
        x=comparacion[
            "Dimensión"
        ],
        y=comparacion[
            territorio_a
        ]
    )
)


fig_comparacion.add_trace(
    go.Bar(
        name=territorio_b,
        x=comparacion[
            "Dimensión"
        ],
        y=comparacion[
            territorio_b
        ]
    )
)


fig_comparacion.update_layout(
    barmode="group",
    yaxis=dict(
        range=[
            0,
            100
        ]
    ),
    yaxis_title="Score 0–100",
    xaxis_title="",
    height=500
)


st.plotly_chart(
    fig_comparacion,
    use_container_width=True
)


# ============================================================
# KPIs COMPARACIÓN
# ============================================================

ca1, ca2, cb1, cb2 = st.columns(4)

with ca1:

    st.metric(
        f"{territorio_a} · IRNA-C",
        f"{fila_a['IRNA_C']:.1f}"
    )

with ca2:

    st.metric(
        f"{territorio_a} · Ranking",
        f"#{int(fila_a['Ranking_IRNA_C'])}"
    )

with cb1:

    st.metric(
        f"{territorio_b} · IRNA-C",
        f"{fila_b['IRNA_C']:.1f}"
    )

with cb2:

    st.metric(
        f"{territorio_b} · Ranking",
        f"#{int(fila_b['Ranking_IRNA_C'])}"
    )


st.divider()


# ============================================================
# RANKING NACIONAL COMPLETO
# ============================================================

st.header(
    "Ranking nacional completo"
)


tabla_ranking = ranking[
    [
        "Ranking_IRNA_C",
        "Departamento",
        "IRNA_C",
        "Categoria_IRNA_C",
        "Score_DEMANDA",
        "Score_DESEMPENO_TURISTICO",
        "Score_CONECTIVIDAD",
        "Score_OFERTA_FORMAL",
        "Score_CAPITAL_NATURAL"
    ]
].copy()


columnas_redondear = [
    "IRNA_C",
    "Score_DEMANDA",
    "Score_DESEMPENO_TURISTICO",
    "Score_CONECTIVIDAD",
    "Score_OFERTA_FORMAL",
    "Score_CAPITAL_NATURAL"
]


for columna in columnas_redondear:

    tabla_ranking[
        columna
    ] = (
        tabla_ranking[
            columna
        ]
        .round(
            1
        )
    )


st.dataframe(
    tabla_ranking,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SENSIBILIDAD NACIONAL
# ============================================================

with st.expander(
    "Ver estabilidad nacional del ranking"
):

    tabla_sensibilidad = sensibilidad[
        [
            "Departamento",
            "Ranking_Base",
            "Ranking_Mejor",
            "Ranking_Peor",
            "Rango_Ranking",
            "Robustez_Ranking"
        ]
    ].copy()

    tabla_sensibilidad = (
        tabla_sensibilidad
        .sort_values(
            "Ranking_Base"
        )
    )

    st.dataframe(
        tabla_sensibilidad,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# METODOLOGÍA
# ============================================================

with st.expander(
    "Metodología resumida del IRNA-C"
):

    st.markdown(
        """
        ### Dimensiones

        El modelo base integra cinco dimensiones:

        **1. Demanda**

        **2. Desempeño turístico**

        **3. Conectividad**

        **4. Oferta formal**

        **5. Capital natural**

        Cada dimensión representa el **20% del IRNA-C**.

        ### Indicadores

        El modelo utiliza **15 indicadores**.

        Los indicadores fueron previamente evaluados para evitar
        redundancias estadísticas.

        ### Normalización

        Los indicadores fueron transformados a una escala
        **0–100**, aplicando:

        - winsorización percentil 5–95;
        - normalización Min-Max.

        ### Sensibilidad

        El ranking fue evaluado bajo **seis escenarios distintos
        de ponderación**.

        Esto permite identificar territorios cuyo resultado es
        robusto y territorios sensibles a cambios metodológicos.

        ### Estado metodológico

        **IRNA-C 2026 es una versión experimental.**

        No constituye todavía un índice oficial.
        """
    )


# ============================================================
# PIE
# ============================================================

st.divider()

st.caption(
    "Radar de Turismo de Naturaleza y Aventura del Perú · "
    "IRNA-C 2026 · MVP experimental"
)