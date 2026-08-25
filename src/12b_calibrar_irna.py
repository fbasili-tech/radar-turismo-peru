from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 12B: CALIBRACIÓN DEL IRNA
# ============================================================

ENTRADA = Path(
    "outputs/radar_turismo_indice_territorial_irna_2026.xlsx"
)

SALIDA = Path(
    "outputs/radar_turismo_irna_calibrado_2026.xlsx"
)


# ============================================================
# PESOS DEL IRNA V2
# ============================================================

PESOS_ESTRUCTURAL = {
    "Inversion": 0.25,
    "Vocacion": 0.25,
    "Masa_Critica": 0.20,
    "Diversidad": 0.15,
    "Evidencia": 0.15
}

PESO_EJECUCION = 1.00


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


def categoria_estructural(valor):

    if valor >= 75:
        return "LÍDER ESTRUCTURAL"

    if valor >= 60:
        return "ALTO POTENCIAL"

    if valor >= 45:
        return "EN CONSOLIDACIÓN"

    return "EMERGENTE"


def categoria_ejecucion(valor):

    if valor >= 80:
        return "MUY ALTA"

    if valor >= 60:
        return "ALTA"

    if valor >= 40:
        return "MEDIA"

    if valor >= 20:
        return "BAJA"

    return "MUY BAJA"


def categoria_brecha(valor):

    if valor >= 30:
        return "BRECHA CRÍTICA"

    if valor >= 15:
        return "BRECHA ALTA"

    if valor >= 5:
        return "BRECHA MODERADA"

    if valor > -5:
        return "EQUILIBRIO"

    return "EJECUCIÓN SUPERIOR AL POTENCIAL"


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():

    print("=" * 100)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("12B - IRNA CALIBRADO")
    print("=" * 100)

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Ranking_IRNA"
    )

    print(
        f"\nTerritorios cargados: {len(df):,}"
    )

    # ========================================================
    # MASA CRÍTICA
    # ========================================================

    df["Score_Registros"] = normalizar_0_100(
        np.log1p(
            df["Registros_Radar"]
        )
    )

    df["Score_Alta_Vocacion"] = normalizar_0_100(
        np.log1p(
            df["Proyectos_Alta_Vocacion"]
        )
    )

    df["Score_Proyectos_Evidencia"] = normalizar_0_100(
        np.log1p(
            df["Proyectos_Con_Evidencia"]
        )
    )

    df["Score_Masa_Critica"] = (
        df["Score_Registros"] * 0.40
        + df["Score_Alta_Vocacion"] * 0.35
        + df["Score_Proyectos_Evidencia"] * 0.25
    )

    # ========================================================
    # IRNA ESTRUCTURAL
    # ========================================================

    df["IRNA_Estructural"] = (
        df["Score_Inversion"]
        * PESOS_ESTRUCTURAL["Inversion"]

        + df["Score_Vocacion"]
        * PESOS_ESTRUCTURAL["Vocacion"]

        + df["Score_Masa_Critica"]
        * PESOS_ESTRUCTURAL["Masa_Critica"]

        + df["Score_Diversidad"]
        * PESOS_ESTRUCTURAL["Diversidad"]

        + df["Score_Evidencia"]
        * PESOS_ESTRUCTURAL["Evidencia"]
    )

    df["IRNA_Estructural"] = (
        df["IRNA_Estructural"]
        .round(1)
    )

    # ========================================================
    # IRNA EJECUCIÓN
    # ========================================================

    df["IRNA_Ejecucion"] = (
        df["Score_Ejecucion"]
        * PESO_EJECUCION
    ).round(1)

    # ========================================================
    # BRECHA
    # ========================================================

    df["Brecha_IRNA"] = (
        df["IRNA_Estructural"]
        - df["IRNA_Ejecucion"]
    ).round(1)

    # ========================================================
    # CATEGORÍAS
    # ========================================================

    df["Categoria_Estructural"] = (
        df["IRNA_Estructural"]
        .apply(categoria_estructural)
    )

    df["Categoria_Ejecucion"] = (
        df["IRNA_Ejecucion"]
        .apply(categoria_ejecucion)
    )

    df["Categoria_Brecha"] = (
        df["Brecha_IRNA"]
        .apply(categoria_brecha)
    )

    # ========================================================
    # RANKINGS
    # ========================================================

    ranking_estructural = (
        df.sort_values(
            "IRNA_Estructural",
            ascending=False
        )
        .reset_index(drop=True)
    )

    ranking_estructural[
        "Ranking_Estructural"
    ] = (
        ranking_estructural.index + 1
    )

    ranking_ejecucion = (
        df.sort_values(
            "IRNA_Ejecucion",
            ascending=False
        )
        .reset_index(drop=True)
    )

    ranking_ejecucion[
        "Ranking_Ejecucion"
    ] = (
        ranking_ejecucion.index + 1
    )

    ranking_brecha = (
        df.sort_values(
            "Brecha_IRNA",
            ascending=False
        )
        .reset_index(drop=True)
    )

    ranking_brecha[
        "Ranking_Brecha"
    ] = (
        ranking_brecha.index + 1
    )

    # ========================================================
    # MATRIZ SÍNTESIS
    # ========================================================

    sintesis = ranking_estructural[
        [
            "Departamento",
            "IRNA_Estructural",
            "Categoria_Estructural",
            "IRNA_Ejecucion",
            "Categoria_Ejecucion",
            "Brecha_IRNA",
            "Categoria_Brecha",
            "PIM_Radar",
            "Registros_Radar",
            "Proyectos_Alta_Vocacion",
            "Proyectos_Con_Evidencia",
            "Diversidad_Ambitos",
            "Diversidad_Intervenciones"
        ]
    ].copy()

    sintesis.insert(
        0,
        "Ranking_Estructural",
        range(1, len(sintesis) + 1)
    )

    # ========================================================
    # MOSTRAR RESULTADOS
    # ========================================================

    print("\n" + "=" * 100)
    print("RANKING IRNA ESTRUCTURAL")
    print("=" * 100)

    print(
        ranking_estructural.head(15)
        [
            [
                "Departamento",
                "IRNA_Estructural",
                "Categoria_Estructural",
                "PIM_Radar",
                "Registros_Radar",
                "Proyectos_Alta_Vocacion",
                "Proyectos_Con_Evidencia"
            ]
        ]
        .to_string(
            index=False,
            formatters={
                "PIM_Radar":
                    lambda x: f"{x:,.0f}"
            }
        )
    )

    print("\n" + "=" * 100)
    print("TOP 10 EJECUCIÓN")
    print("=" * 100)

    print(
        ranking_ejecucion.head(10)
        [
            [
                "Departamento",
                "IRNA_Ejecucion",
                "Categoria_Ejecucion",
                "PIM_Radar"
            ]
        ]
        .to_string(
            index=False,
            formatters={
                "PIM_Radar":
                    lambda x: f"{x:,.0f}"
            }
        )
    )

    print("\n" + "=" * 100)
    print("TOP 10 BRECHAS ENTRE POTENCIAL Y EJECUCIÓN")
    print("=" * 100)

    print(
        ranking_brecha.head(10)
        [
            [
                "Departamento",
                "IRNA_Estructural",
                "IRNA_Ejecucion",
                "Brecha_IRNA",
                "Categoria_Brecha"
            ]
        ]
        .to_string(
            index=False
        )
    )

    # ========================================================
    # CONTROL
    # ========================================================

    print("\n" + "=" * 100)
    print("CONTROL")
    print("=" * 100)

    print(
        f"TERRITORIOS ANALIZADOS : {len(df)}"
    )

    print(
        f"PIM RADAR NACIONAL     : "
        f"S/ {df['PIM_Radar'].sum():,.0f}"
    )

    print(
        f"DEVENGADO RADAR        : "
        f"S/ {df['Devengado_Radar'].sum():,.0f}"
    )

    # ========================================================
    # EXPORTAR
    # ========================================================

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        sintesis.to_excel(
            writer,
            sheet_name="Sintesis_IRNA_V2",
            index=False
        )

        ranking_estructural.to_excel(
            writer,
            sheet_name="Ranking_Estructural",
            index=False
        )

        ranking_ejecucion.to_excel(
            writer,
            sheet_name="Ranking_Ejecucion",
            index=False
        )

        ranking_brecha.to_excel(
            writer,
            sheet_name="Brechas",
            index=False
        )

    print("\nARCHIVO GENERADO:")
    print(SALIDA)

    print(
        "\n✓ IRNA V2 CALIBRADO COMPLETADO"
    )

    print("FIN")


if __name__ == "__main__":
    main()