from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =============================================================================
# RADAR PERÚ
# MÓDULO 08 — DATOS & METODOLOGÍA
#
# OBJETIVO
# -----------------------------------------------------------------------------
# Dar trazabilidad metodológica al sistema RADAR PERÚ:
#
# RESULTADO
#    ↓
# METODOLOGÍA
#    ↓
# VALIDACIÓN
#    ↓
# ALCANCE
#    ↓
# LIMITACIONES
#
# FUENTE
# -----------------------------------------------------------------------------
# outputs/radar_dashboard_ejecutivo_v2_mef_2026.xlsx
#
# HOJAS:
# - 09_Metodologia
# - MEF_Validacion
# - MEF_Metodologia
#
# PRINCIPIOS
# -----------------------------------------------------------------------------
# - No modifica ningún score.
# - No recalcula indicadores.
# - No reemplaza metodologías originales.
# - Expone criterios ya validados.
# =============================================================================


BASE_DIR = Path(__file__).resolve().parents[2]

ARCHIVO = (
    BASE_DIR
    / "outputs"
    / "radar_dashboard_ejecutivo_v2_mef_2026.xlsx"
)


# =============================================================================
# CARGA
# =============================================================================

@st.cache_data
def cargar_metodologia():

    if not ARCHIVO.exists():

        raise FileNotFoundError(
            f"No existe:\n{ARCHIVO}"
        )

    return {

        "general":
            pd.read_excel(
                ARCHIVO,
                sheet_name="09_Metodologia"
            ),

        "mef_validacion":
            pd.read_excel(
                ARCHIVO,
                sheet_name="MEF_Validacion"
            ),

        "mef_metodologia":
            pd.read_excel(
                ARCHIVO,
                sheet_name="MEF_Metodologia"
            ),
    }


# =============================================================================
# UTILIDADES
# =============================================================================

def buscar_valor(
    df,
    columna_clave,
    clave,
    columna_valor
):

    if (
        columna_clave not in df.columns
        or columna_valor not in df.columns
    ):
        return "N/D"

    fila = df[
        df[
            columna_clave
        ]
        .astype(str)
        .str.strip()
        .str.upper()
        ==
        str(clave)
        .strip()
        .upper()
    ]

    if fila.empty:
        return "N/D"

    valor = fila[
        columna_valor
    ].iloc[0]

    if pd.isna(valor):
        return "N/D"

    return str(valor)


# =============================================================================
# RENDER
# =============================================================================

def render_datos_metodologia():

    st.divider()

    st.markdown(
        "## 08 · Datos & Metodología"
    )

    st.caption(
        "Trazabilidad, validación y criterios de interpretación del RADAR."
    )

    try:

        datos = cargar_metodologia()

    except Exception as exc:

        st.error(
            "No fue posible cargar Datos & Metodología."
        )

        st.exception(
            exc
        )

        return


    general = datos[
        "general"
    ].copy()

    mef_validacion = datos[
        "mef_validacion"
    ].copy()

    mef_metodologia = datos[
        "mef_metodologia"
    ].copy()


    # =========================================================================
    # PRINCIPIOS DEL SISTEMA
    # =========================================================================

    st.markdown(
        "### Principios metodológicos del RADAR"
    )


    c1, c2, c3 = st.columns(
        3
    )


    with c1:

        st.metric(
            "IRNA-C",
            buscar_valor(
                general,
                "Tema",
                "IRNA-C",
                "Criterio"
            )
        )


    with c2:

        st.metric(
            "Scores históricos",
            buscar_valor(
                general,
                "Tema",
                "Scores históricos",
                "Criterio"
            )
        )


    with c3:

        st.metric(
            "Validación MEF",
            buscar_valor(
                mef_validacion,
                "Indicador",
                "Resultado metodologico",
                "Valor"
            )
        )


    st.info(
        """
RADAR PERÚ funciona como una capa de inteligencia territorial
que integra resultados previamente validados.

No reemplaza los indicadores originales del sistema ni redefine
los scores históricos.
"""
    )


    # =========================================================================
    # ARQUITECTURA METODOLÓGICA
    # =========================================================================

    st.markdown(
        "### Arquitectura metodológica"
    )


    st.dataframe(
        general,
        hide_index=True,
        width="stretch"
    )


    # =========================================================================
    # RESOURCES / READINESS
    # =========================================================================

    st.markdown(
        "### Construcción de perfiles territoriales"
    )


    resources = buscar_valor(
        general,
        "Tema",
        "Resources",
        "Criterio"
    )


    readiness = buscar_valor(
        general,
        "Tema",
        "Readiness",
        "Criterio"
    )


    r1, r2 = st.columns(
        2
    )


    with r1:

        st.markdown(
            "#### Resources"
        )

        st.write(
            resources
        )


    with r2:

        st.markdown(
            "#### Readiness"
        )

        st.write(
            readiness
        )


    # =========================================================================
    # ATDI
    # =========================================================================

    st.markdown(
        "### Relación con ATTA / ATDI"
    )


    criterio_atdi = buscar_valor(
        general,
        "Tema",
        "ATDI",
        "Criterio"
    )


    st.warning(
        criterio_atdi
    )


    st.caption(
        "El marco ATDI se utiliza como referencia internacional "
        "de alineamiento y benchmarking."
    )


    # =========================================================================
    # METODOLOGÍA MEF
    # =========================================================================

    st.markdown(
        "### Metodología de la capa MEF"
    )


    st.dataframe(
        mef_metodologia,
        hide_index=True,
        width="stretch"
    )


    # =========================================================================
    # PESOS MEF
    # =========================================================================

    pesos_texto = buscar_valor(
        mef_metodologia,
        "Tema",
        "Pesos",
        "Criterio"
    )


    st.markdown(
        "#### Composición del Score MEF"
    )


    st.info(
        pesos_texto
    )


    pesos_df = pd.DataFrame(
        {
            "Componente": [
                "Prioridad estratégica",
                "Déficit relativo de inversión",
                "Brecha de ejecución",
            ],

            "Peso": [
                50,
                30,
                20,
            ]
        }
    )


    fig_pesos = px.bar(
        pesos_df,
        x="Componente",
        y="Peso",
        text="Peso",
        labels={
            "Peso":
                "Peso (%)"
        }
    )


    fig_pesos.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="outside"
    )


    fig_pesos.update_layout(
        height=340,
        yaxis=dict(
            range=[
                0,
                60
            ]
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
        fig_pesos,
        width="stretch"
    )


    # =========================================================================
    # VALIDACIÓN MEF
    # =========================================================================

    st.markdown(
        "### Validación metodológica de la capa MEF"
    )


    st.dataframe(
        mef_validacion,
        hide_index=True,
        width="stretch"
    )


    correlacion = pd.to_numeric(
        pd.Series(
            [
                buscar_valor(
                    mef_validacion,
                    "Indicador",
                    "Correlacion minima escenarios",
                    "Valor"
                )
            ]
        ),
        errors="coerce"
    ).iloc[0]


    variacion = pd.to_numeric(
        pd.Series(
            [
                buscar_valor(
                    mef_validacion,
                    "Indicador",
                    "Variacion promedio ranking",
                    "Valor"
                )
            ]
        ),
        errors="coerce"
    ).iloc[0]


    winsor = pd.to_numeric(
        pd.Series(
            [
                buscar_valor(
                    mef_validacion,
                    "Indicador",
                    "Maximo cambio ranking por winsorizacion",
                    "Valor"
                )
            ]
        ),
        errors="coerce"
    ).iloc[0]


    v1, v2, v3 = st.columns(
        3
    )


    v1.metric(
        "Correlación mínima",
        (
            f"{correlacion:.3f}"
            if pd.notna(
                correlacion
            )
            else "N/D"
        )
    )


    v2.metric(
        "Variación promedio ranking",
        (
            f"{variacion:.2f}"
            if pd.notna(
                variacion
            )
            else "N/D"
        )
    )


    v3.metric(
        "Máx. cambio winsorización",
        (
            f"{winsor:.0f}"
            if pd.notna(
                winsor
            )
            else "N/D"
        )
    )


    # =========================================================================
    # INTERPRETACIÓN
    # =========================================================================

    st.markdown(
        "### Alcance de interpretación"
    )


    st.success(
        """
RADAR PERÚ está diseñado para apoyar:

- priorización territorial;
- identificación de brechas;
- desarrollo de hubs y corredores;
- lectura de inversión pública;
- seguimiento 2026–2030;
- comparación territorial;
- alineamiento con marcos internacionales.
"""
    )


    st.warning(
        """
El sistema no debe interpretarse como:

- un ranking oficial del Estado peruano;
- un ATDI subnacional oficial;
- un reemplazo del análisis de factibilidad de proyectos;
- una medición definitiva de desempeño turístico;
- una sustitución de estudios de mercado, capacidad de carga,
  seguridad, salud o resiliencia climática cuando esas capas
  aún no estén completas.
"""
    )


    # =========================================================================
    # TRAZABILIDAD
    # =========================================================================

    st.markdown(
        "### Trazabilidad de las capas"
    )


    trazabilidad = pd.DataFrame(
        {
            "Capa": [
                "Competitividad territorial",
                "ATTA / ATDI",
                "MEF",
                "Hubs & Corredores",
                "Gestión 2030",
            ],

            "Función": [
                "Diagnóstico territorial",
                "Benchmarking internacional",
                "Decisión de inversión",
                "Articulación multidestino",
                "Ejecución y seguimiento",
            ],

            "Rol dentro del sistema": [
                "Indicador propietario",
                "Marco de referencia",
                "Capa complementaria",
                "Modelo funcional",
                "Hoja de ruta",
            ]
        }
    )


    st.dataframe(
        trazabilidad,
        hide_index=True,
        width="stretch"
    )


    # =========================================================================
    # CIERRE
    # =========================================================================

    st.markdown(
        "### Estado metodológico de RADAR PERÚ V1"
    )


    st.success(
        """
✓ Resultados consolidados

✓ Integración MEF validada

✓ Corredores multidestino integrados

✓ Hoja de ruta 2030 incorporada

✓ ATTA / ATDI tratado como marco de referencia

✓ IRNA-C no modificado

✓ Scores históricos no modificados

✓ Arquitectura preparada para evolución futura
"""
    )


    with st.expander(
        "Notas para evolución futura"
    ):

        st.markdown(
            """
Las siguientes capas pueden fortalecer versiones futuras del Radar:

- seguridad y rescate;
- capacidad sanitaria;
- resiliencia climática;
- percepción e imagen internacional;
- empresas especializadas;
- capacidad de carga;
- tiempos y costos reales de viaje;
- inteligencia predictiva;
- plataforma geoespacial avanzada.

Estas extensiones deben incorporarse como nuevas capas de evidencia,
sin alterar retrospectivamente los indicadores históricos ya validados.
"""
        )