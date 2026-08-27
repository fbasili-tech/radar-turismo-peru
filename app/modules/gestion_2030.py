from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# =============================================================================
# RADAR PERÚ
# MÓDULO 07 — GESTIÓN 2030
#
# OBJETIVO
# -----------------------------------------------------------------------------
# Convertir diagnóstico territorial en hoja de ruta:
#
# BRECHA
#   ↓
# INTERVENCIÓN
#   ↓
# ACTOR / INSTRUMENTO
#   ↓
# FASE
#   ↓
# KPI
#   ↓
# META 2030
#
# FUENTE
# -----------------------------------------------------------------------------
# outputs/radar_dashboard_ejecutivo_v2_mef_2026.xlsx
#
# HOJAS:
# - 04_Brechas_Oportunidades
# - 05_Hoja_Ruta
# - 06_KPI_Seguimiento
#
# PRINCIPIOS
# -----------------------------------------------------------------------------
# - No recalcula scores.
# - No modifica outputs.
# - No inventa metas.
# - No modifica KPI históricos.
# =============================================================================


BASE_DIR = Path(__file__).resolve().parents[2]

ARCHIVO = (
    BASE_DIR
    / "outputs"
    / "radar_dashboard_ejecutivo_v2_mef_2026.xlsx"
)


# =============================================================================
# NORMALIZACIÓN
# =============================================================================

def normalizar(valor):

    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    equivalencias = {
        "ÁNCASH": "ANCASH",
        "ANCASH": "ANCASH",

        "APURÍMAC": "APURIMAC",
        "APURIMAC": "APURIMAC",

        "HUÁNUCO": "HUANUCO",
        "HUANUCO": "HUANUCO",

        "JUNÍN": "JUNIN",
        "JUNIN": "JUNIN",

        "SAN MARTÍN": "SAN MARTIN",
        "SAN MARTIN": "SAN MARTIN",

        "CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO",

        "EL CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO",

        "PROVINCIA CONSTITUCIONAL DEL CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO",
    }

    return equivalencias.get(
        texto,
        texto
    )


def numero(
    fila,
    columna
):

    if columna not in fila.index:
        return np.nan

    try:

        return pd.to_numeric(
            pd.Series(
                [fila[columna]]
            ),
            errors="coerce"
        ).iloc[0]

    except Exception:

        return np.nan


def texto(
    fila,
    columna,
    default="N/D"
):

    if columna not in fila.index:
        return default

    valor = fila[columna]

    if pd.isna(valor):
        return default

    salida = str(valor).strip()

    return salida if salida else default


# =============================================================================
# CARGA
# =============================================================================

@st.cache_data
def cargar_gestion():

    if not ARCHIVO.exists():

        raise FileNotFoundError(
            f"No existe:\n{ARCHIVO}"
        )

    return {

        "brechas":
            pd.read_excel(
                ARCHIVO,
                sheet_name="04_Brechas_Oportunidades"
            ),

        "hoja_ruta":
            pd.read_excel(
                ARCHIVO,
                sheet_name="05_Hoja_Ruta"
            ),

        "kpi":
            pd.read_excel(
                ARCHIVO,
                sheet_name="06_KPI_Seguimiento"
            ),
    }


# =============================================================================
# RENDER
# =============================================================================

def render_gestion_2030(
    territorio
):

    st.divider()

    st.markdown(
        "## 07 · Gestión 2030"
    )

    st.caption(
        "De la brecha territorial a la ejecución y seguimiento."
    )

    try:

        datos = cargar_gestion()

    except Exception as exc:

        st.error(
            "No fue posible cargar Gestión 2030."
        )

        st.exception(
            exc
        )

        return


    brechas = datos[
        "brechas"
    ].copy()

    hoja = datos[
        "hoja_ruta"
    ].copy()

    kpi = datos[
        "kpi"
    ].copy()


    # =========================================================================
    # NORMALIZAR TERRITORIOS
    # =========================================================================

    brechas[
        "_territorio"
    ] = brechas[
        "Departamento"
    ].apply(
        normalizar
    )


    hoja[
        "_territorio"
    ] = hoja[
        "Departamento"
    ].apply(
        normalizar
    )


    kpi[
        "_territorio"
    ] = kpi[
        "Unidad_Seguimiento"
    ].apply(
        normalizar
    )


    territorio_norm = normalizar(
        territorio
    )


    fila_brecha = brechas[
        brechas[
            "_territorio"
        ]
        ==
        territorio_norm
    ]


    fila_hoja = hoja[
        hoja[
            "_territorio"
        ]
        ==
        territorio_norm
    ]


    kpi_t = kpi[
        kpi[
            "_territorio"
        ]
        ==
        territorio_norm
    ].copy()


    if fila_hoja.empty:

        st.warning(
            f"No existe hoja de ruta 2030 para {territorio}."
        )

        return


    fila = fila_hoja.iloc[
        0
    ]


    # =========================================================================
    # VARIABLES
    # =========================================================================

    categoria = texto(
        fila,
        "Categoria_Final_Sistema"
    )

    funcion = texto(
        fila,
        "Funcion_Sistema_2030"
    )

    nivel_intervencion = texto(
        fila,
        "Nivel_Intervencion"
    )

    objetivo = texto(
        fila,
        "Objetivo_2030"
    )

    ranking_sistema = numero(
        fila,
        "Ranking_Sistema_2030"
    )

    ranking_cartera = numero(
        fila,
        "Ranking_Cartera_Territorial"
    )

    prioridad = texto(
        fila,
        "Prioridad_Cartera"
    )

    brecha = texto(
        fila,
        "Brecha_Intervencion"
    )

    intervencion = texto(
        fila,
        "Intervencion"
    )

    actores = texto(
        fila,
        "Actores_Asociados"
    )

    instrumento = texto(
        fila,
        "Instrumento"
    )

    kpi_principal = texto(
        fila,
        "KPI_Principal"
    )

    fase = texto(
        fila,
        "Fase_Implementacion"
    )

    meta_estrategica = texto(
        fila,
        "Meta_Estrategica_2030"
    )

    dependencia = texto(
        fila,
        "Dependencia_Critica"
    )

    estado_inicial = texto(
        fila,
        "Estado_Inicial"
    )

    meta_cuantitativa = texto(
        fila,
        "Meta_Cuantitativa_2030"
    )

    orden = numero(
        fila,
        "Orden_Implementacion"
    )

    score_madurez = numero(
        fila,
        "Score_Madurez_Sistema_2030"
    )


    # =========================================================================
    # CABECERA
    # =========================================================================

    st.markdown(
        f"### Territorio analizado: **{territorio}**"
    )


    c1, c2, c3, c4 = st.columns(
        4
    )


    c1.metric(
        "Prioridad",
        prioridad
    )


    c2.metric(
        "Madurez 2030",
        (
            f"{score_madurez:.1f}"
            if pd.notna(
                score_madurez
            )
            else "N/D"
        )
    )


    c3.metric(
        "Ranking sistema",
        (
            f"#{int(ranking_sistema)}"
            if pd.notna(
                ranking_sistema
            )
            else "N/D"
        )
    )


    c4.metric(
        "Orden implementación",
        (
            f"#{int(orden)}"
            if pd.notna(
                orden
            )
            else "N/D"
        )
    )


    # =========================================================================
    # FUNCIÓN 2030
    # =========================================================================

    st.markdown(
        "### Función dentro del sistema 2030"
    )


    st.info(
        f"""
**Categoría:** {categoria}

**Función:** {funcion}

**Nivel de intervención:** {nivel_intervencion}

**Objetivo 2030:** {objetivo}
"""
    )


    # =========================================================================
    # CADENA DE INTERVENCIÓN
    # =========================================================================

    st.markdown(
        "### Cadena de gestión"
    )


    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

        st.markdown(
            "#### 1. Brecha"
        )

        st.write(
            brecha
        )


    with col2:

        st.markdown(
            "#### 2. Intervención"
        )

        st.write(
            intervencion
        )


    with col3:

        st.markdown(
            "#### 3. Instrumento"
        )

        st.write(
            instrumento
        )


    with col4:

        st.markdown(
            "#### 4. Meta"
        )

        st.write(
            meta_estrategica
        )


    # =========================================================================
    # GOBERNANZA
    # =========================================================================

    st.markdown(
        "### Gobernanza de implementación"
    )


    g1, g2 = st.columns(
        2
    )


    with g1:

        st.markdown(
            "**Actores asociados**"
        )

        st.write(
            actores
        )


        st.markdown(
            "**Fase de implementación**"
        )

        st.write(
            fase
        )


    with g2:

        st.markdown(
            "**Dependencia crítica**"
        )

        st.write(
            dependencia
        )


        st.markdown(
            "**KPI principal**"
        )

        st.write(
            kpi_principal
        )


    # =========================================================================
    # META 2030
    # =========================================================================

    st.markdown(
        "### Meta 2030"
    )


    st.success(
        meta_estrategica
    )


    st.caption(
        f"Estado inicial: {estado_inicial}"
    )


    if meta_cuantitativa != "N/D":

        st.caption(
            f"Meta cuantitativa 2030: {meta_cuantitativa}"
        )


    # =========================================================================
    # KPI TERRITORIALES
    # =========================================================================

    st.markdown(
        "### KPI de seguimiento"
    )


    if kpi_t.empty:

        st.warning(
            "No existen KPI territoriales asociados."
        )

    else:

        columnas_kpi = [
            c
            for c in [
                "ID_KPI",
                "Tipo_KPI",
                "Dimension",
                "KPI",
                "Linea_Base_2026_Cerrada",
                "Meta_2030_Cerrada",
                "Valor_Actual",
                "Semaforo",
                "Periodicidad",
                "Responsable",
                "Estado_Final_KPI",
            ]
            if c in kpi_t.columns
        ]


        st.dataframe(
            kpi_t[
                columnas_kpi
            ],
            hide_index=True,
            width="stretch"
        )


        # =====================================================================
        # VISUAL DE KPI CON BASE Y META
        # =====================================================================

        kpi_graf = kpi_t.copy()


        kpi_graf[
            "Linea_Base_2026_Cerrada"
        ] = pd.to_numeric(
            kpi_graf[
                "Linea_Base_2026_Cerrada"
            ],
            errors="coerce"
        )


        kpi_graf[
            "Meta_2030_Cerrada"
        ] = pd.to_numeric(
            kpi_graf[
                "Meta_2030_Cerrada"
            ],
            errors="coerce"
        )


        graf_largo = kpi_graf[
            [
                "KPI",
                "Linea_Base_2026_Cerrada",
                "Meta_2030_Cerrada",
            ]
        ].melt(
            id_vars="KPI",
            var_name="Serie",
            value_name="Valor"
        )


        graf_largo = graf_largo.dropna(
            subset=[
                "Valor"
            ]
        )


        if not graf_largo.empty:

            fig = px.bar(
                graf_largo,
                x="KPI",
                y="Valor",
                color="Serie",
                barmode="group",
                labels={
                    "Valor":
                        "Valor",

                    "Serie":
                        "Referencia"
                }
            )


            fig.update_layout(
                height=430,
                xaxis_title=None,
                margin=dict(
                    l=0,
                    r=20,
                    t=20,
                    b=80
                )
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )


    # =========================================================================
    # CARTERA NACIONAL
    # =========================================================================

    st.markdown(
        "### Cartera nacional 2030"
    )


    cartera = hoja[
        [
            "Departamento",
            "Ranking_Cartera_Territorial",
            "Prioridad_Cartera",
            "Brecha_Intervencion",
            "Fase_Implementacion",
            "Categoria_Final_Sistema",
            "Orden_Implementacion",
        ]
    ].copy()


    cartera = cartera.sort_values(
        "Orden_Implementacion"
    )


    st.dataframe(
        cartera,
        hide_index=True,
        width="stretch"
    )


    # =========================================================================
    # DISTRIBUCIÓN POR FASE
    # =========================================================================

    st.markdown(
        "### Secuencia de implementación nacional"
    )


    fases = (
        hoja[
            "Fase_Implementacion"
        ]
        .value_counts()
        .reset_index()
    )


    fases.columns = [
        "Fase",
        "Territorios"
    ]


    fig_fases = px.bar(
        fases,
        x="Fase",
        y="Territorios",
        text="Territorios"
    )


    fig_fases.update_traces(
        textposition="outside"
    )


    fig_fases.update_layout(
        height=360,
        xaxis_title=None,
        yaxis_title="Territorios",
        margin=dict(
            l=0,
            r=20,
            t=20,
            b=20
        )
    )


    st.plotly_chart(
        fig_fases,
        width="stretch"
    )


    # =========================================================================
    # METODOLOGÍA
    # =========================================================================

    with st.expander(
        "Cómo interpretar Gestión 2030"
    ):

        st.markdown(
            """
**Brecha de intervención**  
Problema territorial prioritario identificado por el Radar.

**Intervención**  
Tipo de acción propuesta para cerrar la brecha.

**Actor / instrumento**  
Define quién puede liderar o participar y mediante qué instrumento
de gestión pública, promoción, articulación o desarrollo.

**Fase de implementación**  
Orden temporal del proceso 2026–2030.

**KPI**  
Permite convertir una recomendación estratégica en seguimiento.

**Meta 2030**  
Resultado esperado del proceso territorial.

El módulo Gestión 2030 no crea nuevas prioridades.
Organiza y visualiza la hoja de ruta previamente construida
por RADAR PERÚ.
"""
        )