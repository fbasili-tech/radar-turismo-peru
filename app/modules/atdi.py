from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =============================================================================
# RADAR PERÚ
# MÓDULO 04 — ATTA / ATDI ALIGNMENT
#
# PRINCIPIOS METODOLÓGICOS
# -----------------------------------------------------------------------------
# - ATDI funciona como marco internacional de referencia.
# - Los indicadores territoriales pertenecen a RADAR PERÚ.
# - NO se presenta un ATDI territorial oficial.
# - NO se recalculan scores.
# - NO se modifica IRNA-C.
# - Enabling Environment no genera score territorial mientras
#   la cobertura de información sea insuficiente.
# =============================================================================


BASE_DIR = Path(__file__).resolve().parents[2]

ARCHIVO_ATDI = (
    BASE_DIR
    / "outputs"
    / "radar_fase2_competitividad_atta_atdi_2026.xlsx"
)


# =============================================================================
# CARGA
# =============================================================================

@st.cache_data
def cargar_atdi():

    if not ARCHIVO_ATDI.exists():

        raise FileNotFoundError(
            f"No existe el archivo ATDI:\n{ARCHIVO_ATDI}"
        )

    return {

        "mapeo":
            pd.read_excel(
                ARCHIVO_ATDI,
                sheet_name="02_Mapeo_Radar_ATDI"
            ),

        "factores":
            pd.read_excel(
                ARCHIVO_ATDI,
                sheet_name="03_Factores_ATDI"
            ),

        "brechas":
            pd.read_excel(
                ARCHIVO_ATDI,
                sheet_name="04_Brechas_Competitivas"
            ),

        "perfil":
            pd.read_excel(
                ARCHIVO_ATDI,
                sheet_name="05_Perfil_Territorial"
            ),

        "kpi":
            pd.read_excel(
                ARCHIVO_ATDI,
                sheet_name="06_KPI_ATDI"
            ),

        "palancas":
            pd.read_excel(
                ARCHIVO_ATDI,
                sheet_name="07_Palancas_2030"
            ),
    }


# =============================================================================
# UTILIDADES
# =============================================================================

def normalizar(valor):

    if pd.isna(valor):
        return ""

    return str(valor).strip().upper()


def obtener_territorio(
    df,
    territorio
):

    if (
        df is None
        or df.empty
        or "Departamento" not in df.columns
    ):

        return pd.DataFrame()

    return df[
        df["Departamento"]
        .astype(str)
        .map(normalizar)
        ==
        normalizar(territorio)
    ].copy()


def formato_score(valor):

    try:

        if pd.isna(valor):
            return "N/D"

        return f"{float(valor):.1f}"

    except Exception:

        return "N/D"


def obtener_valor(
    fila,
    columna,
    default=None
):

    if columna not in fila.index:
        return default

    valor = fila[columna]

    if pd.isna(valor):
        return default

    return valor


# =============================================================================
# RESUMEN DE COBERTURA ATDI
# =============================================================================

def mostrar_cobertura_atdi(
    mapeo
):

    st.markdown(
        "### Cobertura del marco ATDI"
    )

    st.caption(
        "Muestra cuánto del marco internacional de referencia "
        "está actualmente representado por variables del RADAR."
    )

    cobertura = mapeo[
        [
            "Factor_ATDI",
            "Pilar_ATDI",
            "Cobertura_Radar_Pct",
            "Estado_Cobertura",
            "Peso_Efectivo_ATDI_Pct",
            "Contribucion_Alineamiento_Radar",
        ]
    ].copy()

    cobertura[
        "Cobertura_Radar_Pct"
    ] = pd.to_numeric(
        cobertura[
            "Cobertura_Radar_Pct"
        ],
        errors="coerce"
    )

    cobertura = cobertura.sort_values(
        "Cobertura_Radar_Pct",
        ascending=True
    )

    fig = px.bar(
        cobertura,
        x="Cobertura_Radar_Pct",
        y="Pilar_ATDI",
        orientation="h",
        color="Factor_ATDI",
        text="Cobertura_Radar_Pct",
        labels={
            "Cobertura_Radar_Pct":
                "Cobertura RADAR (%)",

            "Pilar_ATDI":
                "Pilar ATDI",

            "Factor_ATDI":
                "Factor ATDI"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="outside"
    )

    fig.update_layout(
        height=500,
        xaxis=dict(
            range=[0, 105]
        ),
        yaxis_title=None,
        margin=dict(
            l=0,
            r=30,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# =============================================================================
# MAPEO RADAR ↔ ATDI
# =============================================================================

def mostrar_mapeo(
    mapeo
):

    st.markdown(
        "### Mapeo RADAR ↔ ATDI"
    )

    st.caption(
        "Relación metodológica entre los pilares del marco ATDI "
        "y las variables actualmente disponibles en RADAR PERÚ."
    )

    factores = (
        mapeo[
            "Factor_ATDI"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    factor = st.selectbox(
        "Factor ATDI",
        factores,
        key="atdi_factor"
    )

    tabla = mapeo[
        mapeo[
            "Factor_ATDI"
        ]
        ==
        factor
    ].copy()

    columnas = [
        "Pilar_ATDI",
        "Cobertura_Radar_Pct",
        "Estado_Cobertura",
        "Variables_Radar",
        "Brecha_Data",
        "Palanca_Estrategica",
    ]

    columnas = [
        c
        for c in columnas
        if c in tabla.columns
    ]

    st.dataframe(
        tabla[columnas],
        hide_index=True,
        width="stretch"
    )


# =============================================================================
# PERFIL TERRITORIAL
# =============================================================================

def mostrar_perfil_territorial(
    perfil,
    territorio
):

    st.markdown(
        "### Perfil territorial RADAR"
    )

    fila_df = obtener_territorio(
        perfil,
        territorio
    )

    if fila_df.empty:

        st.warning(
            f"No existe perfil ATDI/RADAR para {territorio}."
        )

        return

    fila = fila_df.iloc[0]

    resources = obtener_valor(
        fila,
        "Perfil_Resources_Radar"
    )

    readiness = obtener_valor(
        fila,
        "Perfil_Readiness_Radar"
    )

    enabling = obtener_valor(
        fila,
        "Perfil_Enabling_Environment_Radar"
    )

    competitividad = obtener_valor(
        fila,
        "Perfil_Competitividad_Radar"
    )

    capital = obtener_valor(
        fila,
        "Score_Capital_Natural"
    )

    activacion = obtener_valor(
        fila,
        "Score_Activacion_Turistica"
    )

    accesibilidad = obtener_valor(
        fila,
        "Score_Accesibilidad_Multimodal_V2"
    )

    madurez = obtener_valor(
        fila,
        "Score_Madurez_Sistema_2030"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Resources",
        formato_score(resources)
    )

    c2.metric(
        "Readiness",
        formato_score(readiness)
    )

    c3.metric(
        "Competitividad",
        formato_score(competitividad)
    )

    c4.metric(
        "Enabling Environment",
        formato_score(enabling)
    )

    if pd.isna(enabling):

        cobertura = obtener_valor(
            fila,
            "Cobertura_Enabling_Environment",
            "INSUFICIENTE PARA SCORE TERRITORIAL"
        )

        st.warning(
            "Enabling Environment no se presenta como score "
            f"territorial. Estado de cobertura: {cobertura}."
        )

    st.markdown(
        "#### Capacidades territoriales observadas"
    )

    dimensiones = pd.DataFrame(
        {
            "Dimensión": [
                "Capital Natural",
                "Activación Turística",
                "Accesibilidad Multimodal",
                "Madurez Sistema 2030",
            ],

            "Score": [
                capital,
                activacion,
                accesibilidad,
                madurez,
            ]
        }
    )

    dimensiones[
        "Score"
    ] = pd.to_numeric(
        dimensiones[
            "Score"
        ],
        errors="coerce"
    )

    fig = px.bar(
        dimensiones,
        x="Dimensión",
        y="Score",
        text="Score",
        labels={
            "Score":
                "Score RADAR"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig.update_layout(
        height=380,
        yaxis=dict(
            range=[0, 100]
        ),
        xaxis_title=None,
        margin=dict(
            l=0,
            r=20,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    tipologia = obtener_valor(
        fila,
        "Tipologia_Competitividad_Radar",
        "N/D"
    )

    categoria = obtener_valor(
        fila,
        "Categoria_Final_Sistema",
        "N/D"
    )

    palanca = obtener_valor(
        fila,
        "Palanca_Competitividad",
        "N/D"
    )

    ranking = obtener_valor(
        fila,
        "Ranking_Perfil_Competitividad_Radar"
    )

    st.markdown(
        "#### Lectura estratégica"
    )

    st.info(
        f"""
**Rol territorial:** {categoria}

**Tipología competitiva:** {tipologia}

**Ranking nacional:** {
    f"#{int(ranking)}"
    if pd.notna(ranking)
    else "N/D"
}

**Palanca de competitividad:** {palanca}
"""
    )


# =============================================================================
# BRECHAS DEL MARCO
# =============================================================================

def mostrar_brechas_marco(
    mapeo
):

    st.markdown(
        "### Brechas de información y desarrollo"
    )

    st.caption(
        "Identifica dónde RADAR PERÚ ya posee evidencia "
        "y dónde será necesario incorporar nuevas capas de datos."
    )

    tabla = mapeo[
        [
            "Factor_ATDI",
            "Pilar_ATDI",
            "Cobertura_Radar_Pct",
            "Estado_Cobertura",
            "Brecha_Data",
            "Palanca_Estrategica",
        ]
    ].copy()

    tabla[
        "Cobertura_Radar_Pct"
    ] = pd.to_numeric(
        tabla[
            "Cobertura_Radar_Pct"
        ],
        errors="coerce"
    )

    tabla = tabla.sort_values(
        "Cobertura_Radar_Pct"
    )

    st.dataframe(
        tabla,
        hide_index=True,
        width="stretch"
    )


# =============================================================================
# MATRIZ DE ALINEAMIENTO
# =============================================================================

def mostrar_matriz_alineamiento(
    mapeo
):

    st.markdown(
        "### Matriz de alineamiento internacional"
    )

    matriz = mapeo.pivot_table(
        index="Pilar_ATDI",
        columns="Factor_ATDI",
        values="Cobertura_Radar_Pct",
        aggfunc="mean"
    )

    fig = px.imshow(
        matriz,
        text_auto=".0f",
        aspect="auto",
        labels={
            "x":
                "Factor ATDI",

            "y":
                "Pilar ATDI",

            "color":
                "Cobertura RADAR %"
        },
        zmin=0,
        zmax=100
    )

    fig.update_layout(
        height=500,
        margin=dict(
            l=0,
            r=20,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# =============================================================================
# FUNCIÓN PRINCIPAL DEL MÓDULO
# =============================================================================

def render_atdi(
    territorio
):

    st.divider()

    st.markdown(
        """
        ## 04 · ATTA / ATDI Alignment
        """
    )

    st.caption(
        "Benchmarking internacional y alineamiento metodológico "
        "del sistema RADAR PERÚ."
    )

    st.info(
        """
**Nota metodológica**

ATDI se utiliza como marco internacional de referencia.

Los indicadores territoriales presentados en esta sección son
indicadores propietarios de RADAR PERÚ y **no representan un
ATDI oficial ni un ranking ATDI subnacional**.
"""
    )

    try:

        datos = cargar_atdi()

    except Exception as exc:

        st.error(
            "No fue posible cargar el módulo ATDI."
        )

        st.exception(
            exc
        )

        return

    mapeo = datos[
        "mapeo"
    ]

    perfil = datos[
        "perfil"
    ]

    # -------------------------------------------------------------------------
    # CABECERA
    # -------------------------------------------------------------------------

    st.markdown(
        f"### Territorio analizado: **{territorio}**"
    )

    # -------------------------------------------------------------------------
    # TABS
    # -------------------------------------------------------------------------

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Perfil territorial",
            "Cobertura ATDI",
            "Mapeo RADAR ↔ ATDI",
            "Brechas y palancas",
        ]
    )

    with tab1:

        mostrar_perfil_territorial(
            perfil,
            territorio
        )

    with tab2:

        mostrar_cobertura_atdi(
            mapeo
        )

        mostrar_matriz_alineamiento(
            mapeo
        )

    with tab3:

        mostrar_mapeo(
            mapeo
        )

    with tab4:

        mostrar_brechas_marco(
            mapeo
        )

    st.caption(
        "RADAR PERÚ · Peru Reference Model · "
        "Nature & Adventure Tourism Intelligence"
    )