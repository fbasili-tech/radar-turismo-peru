from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =============================================================================
# RADAR PERÚ
# MÓDULO 06 — HUBS & CORREDORES
#
# OBJETIVO
# -----------------------------------------------------------------------------
# Transformar la lectura departamental en una lectura multidestino.
#
# TERRITORIO
#      ↓
# HUB / ARTICULADOR
#      ↓
# CORREDOR
#      ↓
# COMPATIBILIDAD + COMPLEMENTARIEDAD + CONECTIVIDAD
#      ↓
# BRECHA
#      ↓
# FUNCIÓN ESTRATÉGICA 2030
#
# FUENTE
# -----------------------------------------------------------------------------
# outputs/radar_dashboard_ejecutivo_v2_mef_2026.xlsx
# hoja: 03_Hubs_Corredores
#
# PRINCIPIOS
# -----------------------------------------------------------------------------
# - No recalcula scores.
# - No modifica outputs.
# - No redefine hubs.
# - No inventa corredores.
# - Consume resultados previamente calculados por RADAR PERÚ.
# =============================================================================


BASE_DIR = Path(__file__).resolve().parents[2]

ARCHIVO_DASHBOARD = (
    BASE_DIR
    / "outputs"
    / "radar_dashboard_ejecutivo_v2_mef_2026.xlsx"
)

HOJA = "03_Hubs_Corredores"


# =============================================================================
# NORMALIZACIÓN TERRITORIAL
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

def numero(fila, columna):

    if columna not in fila.index:
        return np.nan

    try:
        return pd.to_numeric(
            pd.Series([fila[columna]]),
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


def formato_score(valor):

    if pd.isna(valor):
        return "N/D"

    return f"{valor:.1f}"


# =============================================================================
# CARGA
# =============================================================================

@st.cache_data
def cargar_corredores():

    if not ARCHIVO_DASHBOARD.exists():

        raise FileNotFoundError(
            f"No existe:\n{ARCHIVO_DASHBOARD}"
        )

    libro = pd.ExcelFile(
        ARCHIVO_DASHBOARD
    )

    if HOJA not in libro.sheet_names:

        raise ValueError(
            f"No existe la hoja {HOJA}"
        )

    df = pd.read_excel(
        ARCHIVO_DASHBOARD,
        sheet_name=HOJA
    )

    columnas_requeridas = [
        "Hub_Articulador",
        "Destino",
        "Tipo_Hub_Origen",
        "Tipo_Hub_Destino",
        "Score_Compatibilidad_V1",
        "Nivel_Compatibilidad_Corredor",
        "Score_Corredor_Multidestino_V2",
        "Clasificacion_Corredor_V2",
        "Rol_Articulador_V2",
        "Oportunidad_Estrategica_Corredor",
        "Ranking_Corredor_V2",
        "Categoria_Final_Sistema",
        "Funcion_Sistema_2030",
    ]

    faltantes = [
        c
        for c in columnas_requeridas
        if c not in df.columns
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas requeridas en "
            f"{HOJA}: {faltantes}"
        )

    df["_hub_norm"] = (
        df["Hub_Articulador"]
        .apply(normalizar)
    )

    df["_destino_norm"] = (
        df["Destino"]
        .apply(normalizar)
    )

    return df


# =============================================================================
# RENDER
# =============================================================================

def render_hubs_corredores(
    territorio
):

    st.divider()

    st.markdown(
        "## 06 · Hubs & Corredores"
    )

    st.caption(
        "Del territorio individual al sistema multidestino."
    )

    try:

        df = cargar_corredores()

    except Exception as exc:

        st.error(
            "No fue posible cargar el módulo "
            "Hubs & Corredores."
        )

        st.exception(exc)

        return


    territorio_norm = normalizar(
        territorio
    )


    # =========================================================================
    # IDENTIFICAR PAPEL DEL TERRITORIO
    # =========================================================================

    como_destino = df[
        df["_destino_norm"]
        ==
        territorio_norm
    ].copy()


    como_hub = df[
        df["_hub_norm"]
        ==
        territorio_norm
    ].copy()


    st.markdown(
        f"### Territorio analizado: **{territorio}**"
    )


    # =========================================================================
    # CASO 1 — TERRITORIO COMO DESTINO
    # =========================================================================

    if not como_destino.empty:

        fila = (
            como_destino
            .sort_values(
                "Ranking_Corredor_V2"
            )
            .iloc[0]
        )


        hub = texto(
            fila,
            "Hub_Articulador"
        )

        tipo_hub = texto(
            fila,
            "Tipo_Hub_Origen"
        )

        tipo_destino = texto(
            fila,
            "Tipo_Hub_Destino"
        )

        score_corredor = numero(
            fila,
            "Score_Corredor_Multidestino_V2"
        )

        ranking = numero(
            fila,
            "Ranking_Corredor_V2"
        )

        compatibilidad = numero(
            fila,
            "Score_Compatibilidad_V1"
        )

        complementariedad = numero(
            fila,
            "Score_Complementariedad_Funcional"
        )

        afinidad = numero(
            fila,
            "Score_Afinidad_Macroregional"
        )

        recursos = numero(
            fila,
            "Score_Complementariedad_Recursos"
        )

        clasificacion = texto(
            fila,
            "Clasificacion_Corredor_V2"
        )

        nivel_compatibilidad = texto(
            fila,
            "Nivel_Compatibilidad_Corredor"
        )

        brecha = texto(
            fila,
            "Brecha_Critica_Destino"
        )

        magnitud_brecha = numero(
            fila,
            "Magnitud_Brecha_Critica_Destino"
        )

        intervencion = texto(
            fila,
            "Tipo_Intervencion_Destino"
        )

        oportunidad = texto(
            fila,
            "Oportunidad_Estrategica_Corredor"
        )

        funcion_2030 = texto(
            fila,
            "Funcion_Sistema_2030"
        )

        categoria_final = texto(
            fila,
            "Categoria_Final_Sistema"
        )

        rol_articulador = texto(
            fila,
            "Rol_Articulador_V2"
        )


        # =====================================================================
        # RESUMEN EJECUTIVO
        # =====================================================================

        st.markdown(
            "### Posición dentro del sistema multidestino"
        )


        c1, c2, c3, c4 = st.columns(4)


        c1.metric(
            "Hub articulador",
            hub
        )


        c2.metric(
            "Score corredor",
            formato_score(
                score_corredor
            )
        )


        c3.metric(
            "Ranking corredor",
            (
                f"#{int(ranking)}"
                if pd.notna(ranking)
                else "N/D"
            )
        )


        c4.metric(
            "Compatibilidad",
            formato_score(
                compatibilidad
            )
        )


        st.info(
            f"""
**Corredor:** {hub} → {territorio}

**Clasificación:** {clasificacion}

**Nivel de compatibilidad:** {nivel_compatibilidad}

**Categoría territorial:** {categoria_final}
"""
        )


        # =====================================================================
        # CADENA ESTRATÉGICA
        # =====================================================================

        st.markdown(
            "### Arquitectura del corredor"
        )


        a1, a2, a3 = st.columns(
            [1, 0.25, 1]
        )


        with a1:

            st.markdown(
                f"""
### {hub}

**{tipo_hub}**

{rol_articulador}
"""
            )


        with a2:

            st.markdown(
                """
<br><br>

# →

""",
                unsafe_allow_html=True
            )


        with a3:

            st.markdown(
                f"""
### {territorio}

**{tipo_destino}**

{categoria_final}
"""
            )


        # =====================================================================
        # DIMENSIONES DEL CORREDOR
        # =====================================================================

        st.markdown(
            "### ¿Por qué este corredor?"
        )


        dimensiones = pd.DataFrame(
            {
                "Dimensión": [
                    "Compatibilidad",
                    "Complementariedad funcional",
                    "Afinidad macroregional",
                    "Complementariedad recursos",
                ],

                "Score": [
                    compatibilidad,
                    complementariedad,
                    afinidad,
                    recursos,
                ]
            }
        )


        dimensiones[
            "Score"
        ] = pd.to_numeric(
            dimensiones["Score"],
            errors="coerce"
        )


        fig_dimensiones = px.bar(
            dimensiones,
            x="Score",
            y="Dimensión",
            orientation="h",
            text="Score",
            range_x=[0, 105]
        )


        fig_dimensiones.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )


        fig_dimensiones.update_layout(
            height=330,
            xaxis_title="Score",
            yaxis_title=None,
            margin=dict(
                l=0,
                r=30,
                t=10,
                b=10
            )
        )


        st.plotly_chart(
            fig_dimensiones,
            width="stretch"
        )


        # =====================================================================
        # CONECTIVIDAD
        # =====================================================================

        st.markdown(
            "### Conectividad y operatividad"
        )


        score_od = numero(
            fila,
            "Score_OD_Aereo"
        )

        score_actividad = numero(
            fila,
            "Score_Actividad_Reciente"
        )

        score_operatividad = numero(
            fila,
            "Score_Operatividad"
        )

        frecuencia = numero(
            fila,
            "Frecuencia_Semanal_Identificada"
        )


        k1, k2, k3, k4 = st.columns(4)


        k1.metric(
            "OD aéreo",
            formato_score(
                score_od
            )
        )


        k2.metric(
            "Actividad reciente",
            formato_score(
                score_actividad
            )
        )


        k3.metric(
            "Operatividad",
            formato_score(
                score_operatividad
            )
        )


        k4.metric(
            "Frecuencia semanal",
            (
                f"{int(frecuencia)}"
                if pd.notna(frecuencia)
                else "N/D"
            )
        )


        estado_aereo = texto(
            fila,
            "Estado_Operatividad_Aerea_2026"
        )


        evidencia = texto(
            fila,
            "Nivel_Evidencia_Operatividad"
        )


        st.caption(
            f"Estado aéreo 2026: {estado_aereo} · "
            f"Nivel de evidencia: {evidencia}"
        )


        # =====================================================================
        # BRECHA Y DECISIÓN
        # =====================================================================

        st.markdown(
            "### Brecha crítica y acción"
        )


        b1, b2 = st.columns(2)


        with b1:

            st.metric(
                "Brecha crítica",
                brecha
            )

            st.metric(
                "Magnitud de brecha",
                formato_score(
                    magnitud_brecha
                )
            )


        with b2:

            st.markdown(
                "**Tipo de intervención**"
            )

            st.write(
                intervencion
            )


        # =====================================================================
        # DECISIÓN 2030
        # =====================================================================

        st.markdown(
            "### Función estratégica 2030"
        )


        st.success(
            funcion_2030
        )


        st.markdown(
            "### Oportunidad estratégica del corredor"
        )


        st.info(
            oportunidad
        )


    # =========================================================================
    # CASO 2 — TERRITORIO COMO HUB
    # =========================================================================

    if not como_hub.empty:

        st.markdown(
            "### Territorio como articulador"
        )


        destinos_hub = (
            como_hub
            .sort_values(
                "Ranking_Corredor_V2"
            )
            .copy()
        )


        score_funcional = pd.to_numeric(
            destinos_hub[
                "Score_Funcional_Hub_Origen"
            ],
            errors="coerce"
        ).mean()


        h1, h2, h3 = st.columns(3)


        h1.metric(
            "Destinos articulados",
            len(
                destinos_hub
            )
        )


        h2.metric(
            "Score funcional hub",
            formato_score(
                score_funcional
            )
        )


        h3.metric(
            "Mejor corredor",
            (
                "#"
                +
                str(
                    int(
                        pd.to_numeric(
                            destinos_hub[
                                "Ranking_Corredor_V2"
                            ],
                            errors="coerce"
                        ).min()
                    )
                )
            )
        )


        # =====================================================================
        # RED DEL HUB
        # =====================================================================

        st.markdown(
            f"### Red articulada desde {territorio}"
        )


        red = destinos_hub[
            [
                "Destino",
                "Score_Corredor_Multidestino_V2",
                "Ranking_Corredor_V2",
                "Clasificacion_Corredor_V2",
                "Nivel_Compatibilidad_Corredor",
                "Brecha_Critica_Destino",
            ]
        ].copy()


        red[
            "Score_Corredor_Multidestino_V2"
        ] = pd.to_numeric(
            red[
                "Score_Corredor_Multidestino_V2"
            ],
            errors="coerce"
        )


        fig_red = px.bar(
            red.sort_values(
                "Score_Corredor_Multidestino_V2"
            ),
            x="Score_Corredor_Multidestino_V2",
            y="Destino",
            orientation="h",
            text="Score_Corredor_Multidestino_V2",
            hover_data=[
                "Ranking_Corredor_V2",
                "Clasificacion_Corredor_V2",
                "Nivel_Compatibilidad_Corredor",
                "Brecha_Critica_Destino",
            ]
        )


        fig_red.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )


        fig_red.update_layout(
            height=max(
                380,
                len(red) * 42
            ),
            xaxis_title=(
                "Score corredor multidestino"
            ),
            yaxis_title=None,
            margin=dict(
                l=0,
                r=30,
                t=10,
                b=10
            )
        )


        st.plotly_chart(
            fig_red,
            width="stretch"
        )


        st.dataframe(
            red.sort_values(
                "Ranking_Corredor_V2"
            ),
            hide_index=True,
            width="stretch"
        )


    # =========================================================================
    # SI EL TERRITORIO NO ESTÁ EN LA MATRIZ
    # =========================================================================

    if (
        como_destino.empty
        and
        como_hub.empty
    ):

        st.warning(
            f"{territorio} todavía no aparece "
            "en la matriz priorizada de corredores."
        )


    # =========================================================================
    # RANKING NACIONAL
    # =========================================================================

    st.markdown(
        "### Ranking nacional de corredores"
    )


    ranking_df = (
        df
        .sort_values(
            "Ranking_Corredor_V2"
        )
        .copy()
    )


    ranking_df[
        "Corredor"
    ] = (
        ranking_df[
            "Hub_Articulador"
        ].astype(str)
        +
        " → "
        +
        ranking_df[
            "Destino"
        ].astype(str)
    )


    top = ranking_df.head(10)


    fig_ranking = px.bar(
        top.sort_values(
            "Score_Corredor_Multidestino_V2"
        ),
        x="Score_Corredor_Multidestino_V2",
        y="Corredor",
        orientation="h",
        text="Score_Corredor_Multidestino_V2",
        hover_data=[
            "Ranking_Corredor_V2",
            "Clasificacion_Corredor_V2",
            "Nivel_Compatibilidad_Corredor",
            "Brecha_Critica_Destino",
        ]
    )


    fig_ranking.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )


    fig_ranking.update_layout(
        height=480,
        xaxis_title=(
            "Score corredor multidestino"
        ),
        yaxis_title=None,
        margin=dict(
            l=0,
            r=30,
            t=10,
            b=10
        )
    )


    st.plotly_chart(
        fig_ranking,
        width="stretch"
    )


    # =========================================================================
    # MATRIZ EJECUTIVA
    # =========================================================================

    with st.expander(
        "Ver matriz nacional de corredores"
    ):

        columnas = [
            "Ranking_Corredor_V2",
            "Hub_Articulador",
            "Destino",
            "Score_Corredor_Multidestino_V2",
            "Clasificacion_Corredor_V2",
            "Nivel_Compatibilidad_Corredor",
            "Brecha_Critica_Destino",
            "Tipo_Intervencion_Destino",
            "Categoria_Final_Sistema",
            "Funcion_Sistema_2030",
        ]


        st.dataframe(
            ranking_df[
                columnas
            ],
            hide_index=True,
            width="stretch"
        )


    # =========================================================================
    # METODOLOGÍA
    # =========================================================================

    with st.expander(
        "Cómo interpretar Hubs & Corredores"
    ):

        st.markdown(
            """
### Lectura del módulo

**Hub articulador**  
Territorio con capacidad para distribuir, conectar o articular
flujos hacia otros destinos.

**Destino**  
Territorio que puede integrarse al sistema mediante una relación
funcional con un hub.

**Compatibilidad**  
Expresa la fortaleza relativa de la relación entre articulador
y destino dentro del modelo Radar.

**Complementariedad funcional**  
Evalúa cuánto pueden complementarse los roles de ambos territorios.

**Complementariedad de recursos**  
Permite identificar combinaciones territoriales que amplían
la diversidad de experiencias.

**Score Corredor Multidestino V2**  
Indicador sintético ya calculado por RADAR PERÚ para priorizar
relaciones multidestino.

**Brecha crítica**  
Identifica el principal factor que limita la activación del destino.

**Función Sistema 2030**  
Define el papel estratégico esperado del territorio dentro
del sistema turístico.

El módulo no supone que la existencia de compatibilidad implique
automáticamente un corredor comercial consolidado. La conectividad,
la operación empresarial, la demanda y la validación de mercado
siguen siendo condiciones necesarias.
"""
        )