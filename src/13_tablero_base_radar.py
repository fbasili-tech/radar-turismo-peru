from pathlib import Path
import pandas as pd

# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 13: TABLERO BASE DEL RADAR
# ============================================================

ENTRADA = Path(
    "outputs/radar_turismo_irna_calibrado_2026.xlsx"
)

SALIDA = Path(
    "outputs/radar_turismo_tablero_base_2026.xlsx"
)


# ============================================================
# FUNCIONES
# ============================================================

def estado_territorial(row):

    estructural = row["IRNA_Estructural"]
    ejecucion = row["IRNA_Ejecucion"]
    brecha = row["Brecha_IRNA"]

    if estructural >= 60 and ejecucion >= 60:
        return "FORTALEZA CONSOLIDADA"

    if estructural >= 60 and brecha >= 30:
        return "ALTO POTENCIAL - EJECUCIÓN CRÍTICA"

    if estructural >= 60 and ejecucion < 60:
        return "ALTO POTENCIAL - REQUIERE ACELERACIÓN"

    if estructural >= 45 and ejecucion >= 60:
        return "EMERGENTE CON BUENA EJECUCIÓN"

    if estructural >= 45 and brecha >= 30:
        return "POTENCIAL CON BRECHA DE GESTIÓN"

    if estructural >= 45:
        return "EN CONSOLIDACIÓN"

    return "EMERGENTE"


def nivel_alerta(row):

    if row["Brecha_IRNA"] >= 30:
        return "ROJA"

    if row["Brecha_IRNA"] >= 15:
        return "NARANJA"

    if row["Brecha_IRNA"] >= 5:
        return "AMARILLA"

    return "VERDE"


def recomendacion(row):

    estado = row["Estado_Territorial"]

    if estado == "FORTALEZA CONSOLIDADA":
        return (
            "Consolidar producto, promoción y articulación "
            "público-privada."
        )

    if estado == "ALTO POTENCIAL - EJECUCIÓN CRÍTICA":
        return (
            "Priorizar destrabe de inversiones, seguimiento "
            "de ejecución y gestión de proyectos."
        )

    if estado == "ALTO POTENCIAL - REQUIERE ACELERACIÓN":
        return (
            "Acelerar ejecución y fortalecer cartera de "
            "productos de naturaleza y aventura."
        )

    if estado == "EMERGENTE CON BUENA EJECUCIÓN":
        return (
            "Ampliar masa crítica de proyectos y fortalecer "
            "diversificación del destino."
        )

    if estado == "POTENCIAL CON BRECHA DE GESTIÓN":
        return (
            "Mejorar capacidad de gestión territorial y "
            "priorizar proyectos de mayor impacto."
        )

    if estado == "EN CONSOLIDACIÓN":
        return (
            "Fortalecer productos, articulación territorial "
            "y calidad de la cartera de inversión."
        )

    return (
        "Desarrollar cartera inicial y mejorar evidencia "
        "territorial de naturaleza y aventura."
    )


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():

    print("=" * 100)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("13 - TABLERO BASE")
    print("=" * 100)

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Sintesis_IRNA_V2"
    )

    print(
        f"\nTerritorios cargados: {len(df):,}"
    )

    # ========================================================
    # VARIABLES ESTRATÉGICAS
    # ========================================================

    df["Estado_Territorial"] = (
        df.apply(
            estado_territorial,
            axis=1
        )
    )

    df["Nivel_Alerta"] = (
        df.apply(
            nivel_alerta,
            axis=1
        )
    )

    df["Recomendacion_Estrategica"] = (
        df.apply(
            recomendacion,
            axis=1
        )
    )

    # ========================================================
    # CUADRANTE POTENCIAL VS EJECUCIÓN
    # ========================================================

    mediana_estructural = (
        df["IRNA_Estructural"]
        .median()
    )

    mediana_ejecucion = (
        df["IRNA_Ejecucion"]
        .median()
    )

    def cuadrante(row):

        estructural_alto = (
            row["IRNA_Estructural"]
            >= mediana_estructural
        )

        ejecucion_alta = (
            row["IRNA_Ejecucion"]
            >= mediana_ejecucion
        )

        if estructural_alto and ejecucion_alta:
            return "Q1 - ALTO POTENCIAL / ALTA EJECUCIÓN"

        if estructural_alto and not ejecucion_alta:
            return "Q2 - ALTO POTENCIAL / BAJA EJECUCIÓN"

        if not estructural_alto and ejecucion_alta:
            return "Q3 - MENOR POTENCIAL / ALTA EJECUCIÓN"

        return "Q4 - MENOR POTENCIAL / BAJA EJECUCIÓN"

    df["Cuadrante_IRNA"] = (
        df.apply(
            cuadrante,
            axis=1
        )
    )

    # ========================================================
    # RANKING NACIONAL
    # ========================================================

    ranking = (
        df.sort_values(
            "IRNA_Estructural",
            ascending=False
        )
        .reset_index(drop=True)
    )

    ranking["Ranking_Radar"] = (
        ranking.index + 1
    )

    columnas_ranking = [
        "Ranking_Radar",
        "Departamento",
        "IRNA_Estructural",
        "Categoria_Estructural",
        "IRNA_Ejecucion",
        "Categoria_Ejecucion",
        "Brecha_IRNA",
        "Categoria_Brecha",
        "Estado_Territorial",
        "Nivel_Alerta",
        "PIM_Radar",
        "Registros_Radar",
        "Proyectos_Alta_Vocacion",
        "Proyectos_Con_Evidencia",
        "Diversidad_Ambitos",
        "Diversidad_Intervenciones",
        "Cuadrante_IRNA",
        "Recomendacion_Estrategica"
    ]

    ranking = ranking[
        columnas_ranking
    ]

    # ========================================================
    # MATRIZ POTENCIAL VS EJECUCIÓN
    # ========================================================

    matriz = ranking[
        [
            "Departamento",
            "IRNA_Estructural",
            "IRNA_Ejecucion",
            "Brecha_IRNA",
            "PIM_Radar",
            "Cuadrante_IRNA",
            "Estado_Territorial",
            "Nivel_Alerta"
        ]
    ].copy()

    matriz = matriz.sort_values(
        [
            "Cuadrante_IRNA",
            "IRNA_Estructural"
        ],
        ascending=[
            True,
            False
        ]
    )

    # ========================================================
    # ALERTAS
    # ========================================================

    alertas = ranking[
        ranking["Nivel_Alerta"]
        .isin(
            [
                "ROJA",
                "NARANJA"
            ]
        )
    ].copy()

    alertas = alertas[
        [
            "Departamento",
            "IRNA_Estructural",
            "IRNA_Ejecucion",
            "Brecha_IRNA",
            "Nivel_Alerta",
            "Estado_Territorial",
            "PIM_Radar",
            "Recomendacion_Estrategica"
        ]
    ]

    alertas = alertas.sort_values(
        "Brecha_IRNA",
        ascending=False
    )

    # ========================================================
    # OPORTUNIDADES
    # ========================================================

    oportunidades = ranking[
        (
            ranking["IRNA_Estructural"] >= 55
        )
        &
        (
            ranking["IRNA_Ejecucion"] >= 50
        )
    ].copy()

    oportunidades = oportunidades[
        [
            "Departamento",
            "IRNA_Estructural",
            "IRNA_Ejecucion",
            "PIM_Radar",
            "Registros_Radar",
            "Estado_Territorial",
            "Cuadrante_IRNA"
        ]
    ]

    # ========================================================
    # RESUMEN NACIONAL
    # ========================================================

    resumen = pd.DataFrame(
        {
            "Indicador": [
                "Territorios analizados",
                "PIM núcleo Radar",
                "Territorios líder estructural",
                "Territorios alto potencial",
                "Alertas rojas",
                "Alertas naranjas",
                "Mediana IRNA estructural",
                "Mediana ejecución"
            ],
            "Valor": [
                len(ranking),

                ranking[
                    "PIM_Radar"
                ].sum(),

                (
                    ranking[
                        "Categoria_Estructural"
                    ]
                    == "LÍDER ESTRUCTURAL"
                ).sum(),

                (
                    ranking[
                        "Categoria_Estructural"
                    ]
                    == "ALTO POTENCIAL"
                ).sum(),

                (
                    ranking[
                        "Nivel_Alerta"
                    ]
                    == "ROJA"
                ).sum(),

                (
                    ranking[
                        "Nivel_Alerta"
                    ]
                    == "NARANJA"
                ).sum(),

                round(
                    mediana_estructural,
                    1
                ),

                round(
                    mediana_ejecucion,
                    1
                )
            ]
        }
    )

    # ========================================================
    # MOSTRAR RESULTADOS
    # ========================================================

    print("\n" + "=" * 100)
    print("TOP 15 DEL RADAR")
    print("=" * 100)

    print(
        ranking.head(15)
        [
            [
                "Ranking_Radar",
                "Departamento",
                "IRNA_Estructural",
                "IRNA_Ejecucion",
                "Brecha_IRNA",
                "Estado_Territorial",
                "Nivel_Alerta"
            ]
        ]
        .to_string(
            index=False
        )
    )

    print("\n" + "=" * 100)
    print("ALERTAS TERRITORIALES")
    print("=" * 100)

    print(
        alertas.head(15)
        .to_string(
            index=False,
            formatters={
                "PIM_Radar":
                    lambda x:
                    f"{x:,.0f}"
            }
        )
    )

    print("\n" + "=" * 100)
    print("OPORTUNIDADES")
    print("=" * 100)

    print(
        oportunidades
        .to_string(
            index=False,
            formatters={
                "PIM_Radar":
                    lambda x:
                    f"{x:,.0f}"
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
        f"TERRITORIOS : {len(ranking)}"
    )

    print(
        f"PIM RADAR   : "
        f"S/ {ranking['PIM_Radar'].sum():,.0f}"
    )

    # ========================================================
    # EXPORTAR EXCEL
    # ========================================================

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        resumen.to_excel(
            writer,
            sheet_name="Resumen_Nacional",
            index=False
        )

        ranking.to_excel(
            writer,
            sheet_name="Ranking_Nacional",
            index=False
        )

        matriz.to_excel(
            writer,
            sheet_name="Potencial_vs_Ejecucion",
            index=False
        )

        alertas.to_excel(
            writer,
            sheet_name="Alertas_Territoriales",
            index=False
        )

        oportunidades.to_excel(
            writer,
            sheet_name="Oportunidades",
            index=False
        )

    print("\nARCHIVO GENERADO:")
    print(SALIDA)

    print(
        "\n✓ TABLERO BASE DEL RADAR COMPLETADO"
    )

    print("FIN")


if __name__ == "__main__":
    main()