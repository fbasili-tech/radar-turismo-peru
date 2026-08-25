from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 12: ÍNDICE TERRITORIAL IRNA
# ============================================================

ENTRADA = Path(
    "outputs/radar_turismo_destinos_refinados_2026.xlsx"
)

SALIDA = Path(
    "outputs/radar_turismo_indice_territorial_irna_2026.xlsx"
)


# ============================================================
# CONFIGURACIÓN DE PESOS
# ============================================================

PESOS = {
    "Inversion": 0.30,
    "Ejecucion": 0.20,
    "Vocacion": 0.25,
    "Evidencia": 0.15,
    "Diversidad": 0.10
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def normalizar_0_100(serie):

    serie = pd.to_numeric(
        serie,
        errors="coerce"
    ).fillna(0)

    minimo = serie.min()
    maximo = serie.max()

    if maximo == minimo:
        return pd.Series(
            [0] * len(serie),
            index=serie.index
        )

    return (
        (serie - minimo)
        / (maximo - minimo)
        * 100
    )


def puntaje_vocacion(valor):

    mapa = {
        "ALTA": 100,
        "MEDIA": 70,
        "BAJA": 40,
        "NO DETERMINADA": 10
    }

    return mapa.get(
        str(valor).strip().upper(),
        10
    )


def puntaje_evidencia(valor):

    mapa = {
        "CONFIRMADO": 100,
        "PROBABLE": 75,
        "POTENCIAL": 50,
        "SIN EVIDENCIA": 10
    }

    return mapa.get(
        str(valor).strip().upper(),
        10
    )


def categoria_irna(puntaje):

    if puntaje >= 75:
        return "LÍDER"

    if puntaje >= 60:
        return "ALTO POTENCIAL"

    if puntaje >= 45:
        return "EN DESARROLLO"

    return "EMERGENTE"


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():

    print("=" * 100)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("ÍNDICE TERRITORIAL IRNA")
    print("=" * 100)

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Base_Refinada_11B"
    )

    print(
        f"\nRegistros cargados: {len(df):,}"
    )

    # ========================================================
    # VARIABLES DE PUNTAJE A NIVEL DE PROYECTO
    # ========================================================

    df["Score_Vocacion"] = (
        df["Vocacion_Territorial_NA"]
        .apply(puntaje_vocacion)
    )

    df["Score_Evidencia"] = (
        df["Nivel_Evidencia_Aventura"]
        .apply(puntaje_evidencia)
    )

    # ========================================================
    # RESUMEN TERRITORIAL BASE
    # ========================================================

    territorial = (
        df.groupby(
            "Departamento",
            as_index=False
        )
        .agg(
            Registros_Radar=(
                "ID_Radar",
                "count"
            ),
            PIM_Radar=(
                "PIM",
                "sum"
            ),
            Devengado_Radar=(
                "Devengado",
                "sum"
            ),
            Score_Vocacion_Promedio=(
                "Score_Vocacion",
                "mean"
            ),
            Score_Evidencia_Promedio=(
                "Score_Evidencia",
                "mean"
            )
        )
    )

    # ========================================================
    # EJECUCIÓN
    # ========================================================

    territorial["Avance_Radar_Porcentaje"] = (
        territorial["Devengado_Radar"]
        / territorial["PIM_Radar"]
        * 100
    ).fillna(0)

    # ========================================================
    # DIVERSIDAD DE ÁMBITOS
    # ========================================================

    diversidad_ambitos = (
        df.groupby("Departamento")
        ["Ambito_Turistico_11B"]
        .nunique()
        .rename("Diversidad_Ambitos")
        .reset_index()
    )

    territorial = territorial.merge(
        diversidad_ambitos,
        on="Departamento",
        how="left"
    )

    # ========================================================
    # DIVERSIDAD DE INTERVENCIONES
    # ========================================================

    if "Intervenciones" in df.columns:

        diversidad_int = (
            df.assign(
                Intervenciones_lista=
                df["Intervenciones"]
                .fillna("")
                .astype(str)
                .str.split(",")
            )
            .explode(
                "Intervenciones_lista"
            )
        )

        diversidad_int[
            "Intervenciones_lista"
        ] = (
            diversidad_int[
                "Intervenciones_lista"
            ]
            .astype(str)
            .str.strip()
        )

        diversidad_int = (
            diversidad_int[
                diversidad_int[
                    "Intervenciones_lista"
                ] != ""
            ]
            .groupby("Departamento")
            ["Intervenciones_lista"]
            .nunique()
            .rename("Diversidad_Intervenciones")
            .reset_index()
        )

        territorial = territorial.merge(
            diversidad_int,
            on="Departamento",
            how="left"
        )

    else:

        territorial[
            "Diversidad_Intervenciones"
        ] = 0

    territorial[
        "Diversidad_Intervenciones"
    ] = (
        territorial[
            "Diversidad_Intervenciones"
        ]
        .fillna(0)
    )

    # ========================================================
    # PROYECTOS DE ALTA VOCACIÓN
    # ========================================================

    alta_vocacion = (
        df.assign(
            Es_Alta_Vocacion=(
                df["Vocacion_Territorial_NA"]
                == "ALTA"
            ).astype(int)
        )
        .groupby(
            "Departamento",
            as_index=False
        )
        .agg(
            Proyectos_Alta_Vocacion=(
                "Es_Alta_Vocacion",
                "sum"
            )
        )
    )

    territorial = territorial.merge(
        alta_vocacion,
        on="Departamento",
        how="left"
    )

    # ========================================================
    # PROYECTOS CON EVIDENCIA
    # ========================================================

    evidencia = (
        df.assign(
            Tiene_Evidencia=(
                df[
                    "Nivel_Evidencia_Aventura"
                ]
                != "SIN EVIDENCIA"
            ).astype(int)
        )
        .groupby(
            "Departamento",
            as_index=False
        )
        .agg(
            Proyectos_Con_Evidencia=(
                "Tiene_Evidencia",
                "sum"
            )
        )
    )

    territorial = territorial.merge(
        evidencia,
        on="Departamento",
        how="left"
    )

    # ========================================================
    # NORMALIZACIÓN DE COMPONENTES
    # ========================================================

    # Inversión:
    # usamos logaritmo para evitar que un departamento
    # con mucho PIM domine completamente el índice.

    territorial[
        "PIM_Log"
    ] = np.log1p(
        territorial["PIM_Radar"]
    )

    territorial[
        "Score_Inversion"
    ] = normalizar_0_100(
        territorial["PIM_Log"]
    )

    # Ejecución ya está naturalmente en escala 0-100
    territorial[
        "Score_Ejecucion"
    ] = (
        territorial[
            "Avance_Radar_Porcentaje"
        ]
        .clip(
            lower=0,
            upper=100
        )
    )

    # Vocación
    territorial[
        "Score_Vocacion"
    ] = (
        territorial[
            "Score_Vocacion_Promedio"
        ]
        .clip(
            lower=0,
            upper=100
        )
    )

    # Evidencia
    territorial[
        "Score_Evidencia"
    ] = (
        territorial[
            "Score_Evidencia_Promedio"
        ]
        .clip(
            lower=0,
            upper=100
        )
    )

    # Diversidad combinada
    territorial[
        "Diversidad_Total"
    ] = (
        territorial[
            "Diversidad_Ambitos"
        ]
        + territorial[
            "Diversidad_Intervenciones"
        ]
    )

    territorial[
        "Score_Diversidad"
    ] = normalizar_0_100(
        territorial[
            "Diversidad_Total"
        ]
    )

    # ========================================================
    # CÁLCULO DEL IRNA
    # ========================================================

    territorial[
        "IRNA"
    ] = (
        territorial[
            "Score_Inversion"
        ]
        * PESOS["Inversion"]

        + territorial[
            "Score_Ejecucion"
        ]
        * PESOS["Ejecucion"]

        + territorial[
            "Score_Vocacion"
        ]
        * PESOS["Vocacion"]

        + territorial[
            "Score_Evidencia"
        ]
        * PESOS["Evidencia"]

        + territorial[
            "Score_Diversidad"
        ]
        * PESOS["Diversidad"]
    )

    territorial[
        "IRNA"
    ] = (
        territorial["IRNA"]
        .round(1)
    )

    territorial[
        "Categoria_IRNA"
    ] = (
        territorial["IRNA"]
        .apply(categoria_irna)
    )

    # ========================================================
    # RANKING
    # ========================================================

    territorial = (
        territorial
        .sort_values(
            "IRNA",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    territorial[
        "Ranking_IRNA"
    ] = (
        territorial.index
        + 1
    )

    # Reordenar ranking al inicio
    columnas = [
        "Ranking_IRNA",
        "Departamento",
        "IRNA",
        "Categoria_IRNA",
        "Registros_Radar",
        "PIM_Radar",
        "Devengado_Radar",
        "Avance_Radar_Porcentaje",
        "Proyectos_Alta_Vocacion",
        "Proyectos_Con_Evidencia",
        "Diversidad_Ambitos",
        "Diversidad_Intervenciones",
        "Score_Inversion",
        "Score_Ejecucion",
        "Score_Vocacion",
        "Score_Evidencia",
        "Score_Diversidad"
    ]

    territorial = territorial[
        columnas
    ]

    # ========================================================
    # RESUMEN POR CATEGORÍA
    # ========================================================

    resumen_categoria = (
        territorial
        .groupby(
            "Categoria_IRNA",
            as_index=False
        )
        .agg(
            Territorios=(
                "Departamento",
                "count"
            ),
            PIM_Radar=(
                "PIM_Radar",
                "sum"
            ),
            IRNA_Promedio=(
                "IRNA",
                "mean"
            )
        )
    )

    # ========================================================
    # MOSTRAR TOP 15
    # ========================================================

    print("\n" + "=" * 100)
    print("RANKING NACIONAL IRNA")
    print("=" * 100)

    print(
        territorial.head(15)
        [
            [
                "Ranking_IRNA",
                "Departamento",
                "IRNA",
                "Categoria_IRNA",
                "PIM_Radar",
                "Avance_Radar_Porcentaje",
                "Proyectos_Alta_Vocacion",
                "Proyectos_Con_Evidencia"
            ]
        ]
        .to_string(
            index=False,
            formatters={
                "PIM_Radar":
                    lambda x:
                    f"{x:,.0f}",

                "Avance_Radar_Porcentaje":
                    lambda x:
                    f"{x:.1f}%"
            }
        )
    )

    # ========================================================
    # TOP 5 FORTALEZAS
    # ========================================================

    print("\n" + "=" * 100)
    print("TOP 5 POR COMPONENTE")
    print("=" * 100)

    componentes = {
        "INVERSIÓN":
            "Score_Inversion",

        "EJECUCIÓN":
            "Score_Ejecucion",

        "VOCACIÓN":
            "Score_Vocacion",

        "EVIDENCIA":
            "Score_Evidencia",

        "DIVERSIDAD":
            "Score_Diversidad"
    }

    for nombre, columna in componentes.items():

        print(
            f"\n{nombre}:"
        )

        top = (
            territorial
            .sort_values(
                columna,
                ascending=False
            )
            .head(5)
        )

        print(
            top[
                [
                    "Departamento",
                    columna
                ]
            ]
            .to_string(
                index=False,
                formatters={
                    columna:
                        lambda x:
                        f"{x:.1f}"
                }
            )
        )

    # ========================================================
    # CONTROL
    # ========================================================

    print("\n" + "=" * 100)
    print("CONTROL")
    print("=" * 100)

    print(
        f"TERRITORIOS ANALIZADOS : "
        f"{len(territorial)}"
    )

    print(
        f"PIM RADAR NACIONAL     : "
        f"S/ {territorial['PIM_Radar'].sum():,.0f}"
    )

    print(
        f"DEVENGADO RADAR        : "
        f"S/ {territorial['Devengado_Radar'].sum():,.0f}"
    )

    # ========================================================
    # EXPORTAR
    # ========================================================

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        territorial.to_excel(
            writer,
            sheet_name="Ranking_IRNA",
            index=False
        )

        resumen_categoria.to_excel(
            writer,
            sheet_name="Categorias_IRNA",
            index=False
        )

        df.to_excel(
            writer,
            sheet_name="Base_IRNA",
            index=False
        )

    print("\nARCHIVO GENERADO:")
    print(SALIDA)

    print(
        "\n✓ ÍNDICE TERRITORIAL IRNA COMPLETADO"
    )

    print("FIN")


if __name__ == "__main__":
    main()