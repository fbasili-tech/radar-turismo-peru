from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# =============================================================================
# RADAR PERÚ
# MÓDULO 05 — INVERSIÓN INTELIGENTE
#
# FUENTE:
# outputs/radar_fase3_integracion_mef_2026.xlsx
#
# HOJA PRINCIPAL:
# 03_MEF_Radar
#
# PRINCIPIOS:
# - No recalcula scores
# - No modifica IRNA-C
# - No modifica outputs
# - Consume resultados MEF ya validados
# =============================================================================


BASE_DIR = Path(__file__).resolve().parents[2]

ARCHIVO_MEF = (
    BASE_DIR
    / "outputs"
    / "radar_fase3_integracion_mef_2026.xlsx"
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


# =============================================================================
# UTILIDADES
# =============================================================================

def numero(
    fila,
    columna
):

    if columna is None:
        return np.nan

    try:

        return pd.to_numeric(
            pd.Series(
                [
                    fila.get(
                        columna,
                        np.nan
                    )
                ]
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

    if columna is None:
        return default

    valor = fila.get(
        columna,
        default
    )

    if pd.isna(valor):
        return default

    salida = str(
        valor
    ).strip()

    return salida if salida else default


# =============================================================================
# CARGA
# =============================================================================

@st.cache_data
def cargar_inversion():

    if not ARCHIVO_MEF.exists():

        raise FileNotFoundError(
            f"No existe:\n{ARCHIVO_MEF}"
        )

    libro = pd.ExcelFile(
        ARCHIVO_MEF
    )

    requeridas = [
        "03_MEF_Radar",
        "04_Matriz_Ejecutiva",
        "05_Proyectos_MEF",
    ]

    faltantes = [
        hoja
        for hoja in requeridas
        if hoja not in libro.sheet_names
    ]

    if faltantes:

        raise ValueError(
            f"Faltan hojas MEF requeridas: {faltantes}"
        )

    return {

        "territorial":
            pd.read_excel(
                ARCHIVO_MEF,
                sheet_name="03_MEF_Radar"
            ),

        "matriz":
            pd.read_excel(
                ARCHIVO_MEF,
                sheet_name="04_Matriz_Ejecutiva"
            ),

        "proyectos":
            pd.read_excel(
                ARCHIVO_MEF,
                sheet_name="05_Proyectos_MEF"
            ),
    }


# =============================================================================
# RENDER
# =============================================================================

def render_inversion(
    territorio
):

    st.divider()

    st.markdown(
        "## 05 · Inversión Inteligente"
    )

    st.caption(
        "Prioridad estratégica × inversión pública × ejecución."
    )

    try:

        datos = cargar_inversion()

    except Exception as exc:

        st.error(
            "No fue posible cargar el módulo de inversión."
        )

        st.exception(
            exc
        )

        return


    df = datos[
        "territorial"
    ].copy()

    matriz = datos[
        "matriz"
    ].copy()

    proyectos = datos[
        "proyectos"
    ].copy()


    # =========================================================================
    # VALIDACIÓN DE COLUMNAS
    # =========================================================================

    requeridas = [
        "Departamento",
        "PIM_MEF",
        "Devengado_MEF",
        "Avance_MEF_Pct",
        "Score_Prioridad_Estrategica_100",
        "Score_Inversion_MEF_100",
        "Gap_Prioridad_Inversion",
        "Score_Oportunidad_Inversion_MEF",
        "Categoria_Alineamiento_MEF",
        "Decision_Estrategica_MEF",
    ]

    faltantes = [
        columna
        for columna in requeridas
        if columna not in df.columns
    ]

    if faltantes:

        st.error(
            "La hoja 03_MEF_Radar no contiene "
            f"las columnas esperadas: {faltantes}"
        )

        return


    # =========================================================================
    # TERRITORIO
    # =========================================================================

    df[
        "_territorio"
    ] = df[
        "Departamento"
    ].apply(
        normalizar
    )


    fila_df = df[
        df[
            "_territorio"
        ]
        ==
        normalizar(
            territorio
        )
    ]


    if fila_df.empty:

        st.warning(
            f"No existe información MEF para {territorio}."
        )

        return


    fila = fila_df.iloc[
        0
    ]


    # =========================================================================
    # MÉTRICAS
    # =========================================================================

    pim = numero(
        fila,
        "PIM_MEF"
    )

    devengado = numero(
        fila,
        "Devengado_MEF"
    )

    avance = numero(
        fila,
        "Avance_MEF_Pct"
    )

    prioridad = numero(
        fila,
        "Score_Prioridad_Estrategica_100"
    )

    score_inversion = numero(
        fila,
        "Score_Inversion_MEF_100"
    )

    gap = numero(
        fila,
        "Gap_Prioridad_Inversion"
    )

    oportunidad = numero(
        fila,
        "Score_Oportunidad_Inversion_MEF"
    )

    categoria = texto(
        fila,
        "Categoria_Alineamiento_MEF"
    )

    decision = texto(
        fila,
        "Decision_Estrategica_MEF"
    )

    ranking_oportunidad = numero(
        fila,
        "Ranking_Oportunidad_MEF"
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
        "PIM",
        (
            f"S/ {pim / 1_000_000:.2f} M"
            if pd.notna(
                pim
            )
            else "N/D"
        )
    )


    c2.metric(
        "Devengado",
        (
            f"S/ {devengado / 1_000_000:.2f} M"
            if pd.notna(
                devengado
            )
            else "N/D"
        )
    )


    c3.metric(
        "Ejecución",
        (
            f"{avance:.1f}%"
            if pd.notna(
                avance
            )
            else "N/D"
        )
    )


    c4.metric(
        "Score oportunidad",
        (
            f"{oportunidad:.1f}"
            if pd.notna(
                oportunidad
            )
            else "N/D"
        )
    )


    # =========================================================================
    # CUADRANTE
    # =========================================================================

    st.markdown(
        "### Prioridad estratégica × inversión pública"
    )

    st.caption(
        "Permite distinguir dónde priorizar nueva cartera, "
        "dónde acelerar ejecución y dónde consolidar resultados."
    )


    grafico_df = df.copy()


    grafico_df[
        "Score_Prioridad_Estrategica_100"
    ] = pd.to_numeric(
        grafico_df[
            "Score_Prioridad_Estrategica_100"
        ],
        errors="coerce"
    )


    grafico_df[
        "Score_Inversion_MEF_100"
    ] = pd.to_numeric(
        grafico_df[
            "Score_Inversion_MEF_100"
        ],
        errors="coerce"
    )


    grafico_df[
        "Score_Oportunidad_Inversion_MEF"
    ] = pd.to_numeric(
        grafico_df[
            "Score_Oportunidad_Inversion_MEF"
        ],
        errors="coerce"
    )


    fig = px.scatter(
        grafico_df,
        x="Score_Inversion_MEF_100",
        y="Score_Prioridad_Estrategica_100",

        size="Score_Oportunidad_Inversion_MEF",

        hover_name="Departamento",

        hover_data={
            "PIM_MEF": ":,.0f",
            "Avance_MEF_Pct": ":.1f",
            "Gap_Prioridad_Inversion": ":.1f",
            "Categoria_Alineamiento_MEF": True,
            "Decision_Estrategica_MEF": True,
        },

        labels={
            "Score_Inversion_MEF_100":
                "Score inversión MEF",

            "Score_Prioridad_Estrategica_100":
                "Prioridad estratégica",

            "Score_Oportunidad_Inversion_MEF":
                "Oportunidad"
        }
    )


    promedio_x = grafico_df[
        "Score_Inversion_MEF_100"
    ].mean()


    promedio_y = grafico_df[
        "Score_Prioridad_Estrategica_100"
    ].mean()


    fig.add_vline(
        x=promedio_x,
        line_dash="dash"
    )


    fig.add_hline(
        y=promedio_y,
        line_dash="dash"
    )


    fig.update_layout(
        height=570,
        xaxis=dict(
            range=[
                0,
                105
            ]
        ),
        yaxis=dict(
            range=[
                0,
                105
            ]
        ),
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


    # =========================================================================
    # LECTURA DEL TERRITORIO
    # =========================================================================

    g1, g2, g3, g4 = st.columns(
        4
    )


    g1.metric(
        "Prioridad estratégica",
        (
            f"{prioridad:.1f}"
            if pd.notna(
                prioridad
            )
            else "N/D"
        )
    )


    g2.metric(
        "Score inversión MEF",
        (
            f"{score_inversion:.1f}"
            if pd.notna(
                score_inversion
            )
            else "N/D"
        )
    )


    g3.metric(
        "Gap prioridad / inversión",
        (
            f"{gap:+.1f}"
            if pd.notna(
                gap
            )
            else "N/D"
        )
    )


    g4.metric(
        "Ranking oportunidad",
        (
            f"#{int(ranking_oportunidad)}"
            if pd.notna(
                ranking_oportunidad
            )
            else "N/D"
        )
    )


    # =========================================================================
    # DECISIÓN
    # =========================================================================

    st.markdown(
        "### Lectura estratégica"
    )


    st.info(
        f"""
**Categoría de alineamiento:** {categoria}

**Decisión estratégica sugerida:** {decision}
"""
    )


    # =========================================================================
    # TOP OPORTUNIDADES
    # =========================================================================

    st.markdown(
        "### Top oportunidades nacionales"
    )


    tabla = matriz.copy()


    if (
        "Ranking_Oportunidad_MEF"
        in tabla.columns
    ):

        tabla = tabla.sort_values(
            "Ranking_Oportunidad_MEF"
        )


    tabla = tabla.head(
        10
    )


    columnas_tabla = [
        columna
        for columna in [
            "Ranking_Oportunidad_MEF",
            "Departamento",
            "Categoria_Final_Sistema",
            "Prioridad_Cartera",
            "PIM_MEF",
            "Avance_MEF_Pct",
            "Score_Prioridad_Estrategica_100",
            "Score_Inversion_MEF_100",
            "Gap_Prioridad_Inversion",
            "Score_Oportunidad_Inversion_MEF",
            "Categoria_Alineamiento_MEF",
            "Decision_Estrategica_MEF",
        ]
        if columna in tabla.columns
    ]


    st.dataframe(
        tabla[
            columnas_tabla
        ],
        hide_index=True,
        width="stretch"
    )


    # =========================================================================
    # PROYECTOS DEL TERRITORIO
    # =========================================================================

    if (
        "Departamento_Radar"
        in proyectos.columns
    ):

        proyectos[
            "_territorio"
        ] = proyectos[
            "Departamento_Radar"
        ].apply(
            normalizar
        )


        proyectos_t = proyectos[
            proyectos[
                "_territorio"
            ]
            ==
            normalizar(
                territorio
            )
        ].copy()


        if not proyectos_t.empty:

            st.markdown(
                "### Proyectos MEF del territorio"
            )


            columnas_proyectos = [
                columna
                for columna in [
                    "Ranking_Proyecto_MEF",
                    "CUI_MEF",
                    "Proyecto_MEF",
                    "Nivel_Gobierno_MEF",
                    "Entidad_MEF",
                    "PIM_MEF",
                    "Devengado_MEF",
                    "Avance_MEF_Pct",
                ]
                if columna
                in proyectos_t.columns
            ]


            proyectos_t = proyectos_t.sort_values(
                (
                    "Ranking_Proyecto_MEF"
                    if
                    "Ranking_Proyecto_MEF"
                    in proyectos_t.columns
                    else "PIM_MEF"
                )
            )


            st.dataframe(
                proyectos_t[
                    columnas_proyectos
                ],
                hide_index=True,
                width="stretch"
            )


    # =========================================================================
    # METODOLOGÍA
    # =========================================================================

    with st.expander(
        "Cómo interpretar este módulo"
    ):

        st.markdown(
            """
**Alta prioridad / baja inversión**  
Territorios donde existe una brecha entre importancia estratégica
y recursos públicos asignados. Pueden requerir nueva cartera,
preinversión o estructuración de proyectos.

**Alta inversión / baja ejecución**  
Territorios donde el problema no es necesariamente la disponibilidad
presupuestal, sino la capacidad para convertirla en ejecución.

**Inversión alineada con prioridad**  
Territorios donde prioridad e inversión presentan mayor coherencia.
La gestión se orienta a consolidar y monitorear resultados.

**Gap prioridad / inversión**  
Un valor positivo indica que la prioridad estratégica supera
relativamente el nivel de inversión observado.

Este módulo es una capa complementaria de decisión.
No modifica los scores históricos del RADAR.
"""
        )