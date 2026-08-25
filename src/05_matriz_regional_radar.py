from pathlib import Path
import pandas as pd
import unicodedata
import re

ENTRADA = Path("outputs/radar_turismo_base_maestra_2026.xlsx")
SALIDA = Path("outputs/radar_turismo_matriz_regional_2026.xlsx")


def normalizar(texto):
    if pd.isna(texto):
        return ""

    texto = str(texto).lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


PALABRAS_NATURALEZA = [
    "naturaleza",
    "natural",
    "bosque",
    "selva",
    "amazon",
    "laguna",
    "lago",
    "rio",
    "catarata",
    "cascada",
    "humedal",
    "manglar",
    "montana",
    "cordillera",
    "nevado",
    "glaciar",
    "canon",
    "quebrada",
    "valle",
    "playa",
    "isla",
    "reserva",
    "parque nacional",
    "area natural",
    "biodiversidad",
    "fauna",
    "flora",
    "ecoturismo",
]

PALABRAS_AVENTURA = [
    "aventura",
    "trekking",
    "senderismo",
    "caminata",
    "sendero",
    "montanismo",
    "andinismo",
    "escalada",
    "rapel",
    "rappel",
    "canotaje",
    "rafting",
    "kayak",
    "ciclismo",
    "bicicleta",
    "mountain bike",
    "parapente",
    "tirolesa",
    "zipline",
    "surf",
    "buceo",
    "snorkel",
    "cabalgata",
    "campamento",
    "camping",
    "sandboard",
]


def contiene(texto, palabras):
    return any(p in texto for p in palabras)


def prioridad_territorial(fila):

    peso_na = fila["Peso_PIM_NA_Porcentaje"]
    pim_na = fila["PIM_Naturaleza_Aventura"]
    proyectos_na = fila["Registros_Naturaleza_Aventura"]

    puntaje = 0

    if peso_na >= 60:
        puntaje += 3
    elif peso_na >= 40:
        puntaje += 2
    elif peso_na >= 20:
        puntaje += 1

    if pim_na >= 20_000_000:
        puntaje += 3
    elif pim_na >= 10_000_000:
        puntaje += 2
    elif pim_na >= 3_000_000:
        puntaje += 1

    if proyectos_na >= 20:
        puntaje += 3
    elif proyectos_na >= 10:
        puntaje += 2
    elif proyectos_na >= 5:
        puntaje += 1

    if puntaje >= 7:
        return "MUY ALTA"
    elif puntaje >= 5:
        return "ALTA"
    elif puntaje >= 3:
        return "MEDIA"
    else:
        return "BAJA"


def main():

    print("=" * 80)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("MATRIZ REGIONAL")
    print("=" * 80)

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Base_Maestra"
    )

    print(f"\nRegistros cargados: {len(df):,}")

    # ------------------------------------------------------
    # CLASIFICACIÓN SIMPLE DE NATURALEZA / AVENTURA
    # ------------------------------------------------------

    texto = df["Proyecto"].fillna("").astype(str).apply(normalizar)

    df["Es_Naturaleza"] = texto.apply(
        lambda x: contiene(x, PALABRAS_NATURALEZA)
    )

    df["Es_Aventura"] = texto.apply(
        lambda x: contiene(x, PALABRAS_AVENTURA)
    )

    df["Es_Naturaleza_Aventura"] = (
        df["Es_Naturaleza"] | df["Es_Aventura"]
    )

    # ------------------------------------------------------
    # BASE REGIONAL GENERAL
    # ------------------------------------------------------

    regional = (
        df.groupby("Departamento", as_index=False)
        .agg(
            Registros=("ID_Radar", "count"),
            PIM=("PIM", "sum"),
            Devengado=("Devengado", "sum"),
        )
    )

    regional["Saldo_por_Ejecutar"] = (
        regional["PIM"] - regional["Devengado"]
    )

    regional["Avance_Porcentaje"] = (
        regional["Devengado"]
        / regional["PIM"]
        * 100
    ).fillna(0)

    # ------------------------------------------------------
    # INDICADORES NATURALEZA / AVENTURA
    # ------------------------------------------------------

    na = df[
        df["Es_Naturaleza_Aventura"]
    ].copy()

    regional_na = (
        na.groupby("Departamento", as_index=False)
        .agg(
            Registros_Naturaleza_Aventura=("ID_Radar", "count"),
            PIM_Naturaleza_Aventura=("PIM", "sum"),
            Devengado_Naturaleza_Aventura=("Devengado", "sum"),
        )
    )

    regional = regional.merge(
        regional_na,
        on="Departamento",
        how="left"
    )

    columnas_na = [
        "Registros_Naturaleza_Aventura",
        "PIM_Naturaleza_Aventura",
        "Devengado_Naturaleza_Aventura",
    ]

    regional[columnas_na] = (
        regional[columnas_na]
        .fillna(0)
    )

    regional["Peso_PIM_NA_Porcentaje"] = (
        regional["PIM_Naturaleza_Aventura"]
        / regional["PIM"]
        * 100
    ).fillna(0)

    regional["Avance_NA_Porcentaje"] = (
        regional["Devengado_Naturaleza_Aventura"]
        / regional["PIM_Naturaleza_Aventura"]
        * 100
    ).fillna(0)

    # ------------------------------------------------------
    # NATURALEZA Y AVENTURA POR SEPARADO
    # ------------------------------------------------------

    nat = (
        df[df["Es_Naturaleza"]]
        .groupby("Departamento")
        .size()
        .rename("Registros_Naturaleza")
    )

    ave = (
        df[df["Es_Aventura"]]
        .groupby("Departamento")
        .size()
        .rename("Registros_Aventura")
    )

    regional = regional.merge(
        nat,
        on="Departamento",
        how="left"
    )

    regional = regional.merge(
        ave,
        on="Departamento",
        how="left"
    )

    regional[
        ["Registros_Naturaleza", "Registros_Aventura"]
    ] = regional[
        ["Registros_Naturaleza", "Registros_Aventura"]
    ].fillna(0)

    # ------------------------------------------------------
    # PRIORIZACIÓN TERRITORIAL
    # ------------------------------------------------------

    regional["Prioridad_Territorial"] = (
        regional.apply(
            prioridad_territorial,
            axis=1
        )
    )

    # ------------------------------------------------------
    # RANKINGS
    # ------------------------------------------------------

    regional["Ranking_PIM_NA"] = (
        regional["PIM_Naturaleza_Aventura"]
        .rank(
            ascending=False,
            method="min"
        )
        .astype(int)
    )

    regional["Ranking_Proyectos_NA"] = (
        regional["Registros_Naturaleza_Aventura"]
        .rank(
            ascending=False,
            method="min"
        )
        .astype(int)
    )

    regional = regional.sort_values(
        "PIM_Naturaleza_Aventura",
        ascending=False
    )

    # ------------------------------------------------------
    # CONTROL NACIONAL
    # ------------------------------------------------------

    pim_total = df["PIM"].sum()
    dev_total = df["Devengado"].sum()

    pim_na = na["PIM"].sum()
    dev_na = na["Devengado"].sum()

    print("\n" + "=" * 80)
    print("CONTROL NACIONAL")
    print("=" * 80)

    print(f"PIM TOTAL              : S/ {pim_total:,.0f}")
    print(f"DEVENGADO TOTAL        : S/ {dev_total:,.0f}")

    print(f"\nPIM NATURALEZA/AVENTURA: S/ {pim_na:,.0f}")
    print(f"DEVENGADO N/A          : S/ {dev_na:,.0f}")

    peso_nacional = (
        pim_na / pim_total * 100
        if pim_total else 0
    )

    print(
        f"PESO N/A SOBRE PIM     : {peso_nacional:.1f}%"
    )

    print(
        f"REGISTROS N/A          : {len(na):,} de {len(df):,}"
    )

    # ------------------------------------------------------
    # TOP 10
    # ------------------------------------------------------

    print("\n" + "=" * 80)
    print("TOP 10 DEPARTAMENTOS - PIM NATURALEZA / AVENTURA")
    print("=" * 80)

    top10 = regional[
        [
            "Departamento",
            "Registros_Naturaleza_Aventura",
            "PIM_Naturaleza_Aventura",
            "Devengado_Naturaleza_Aventura",
            "Peso_PIM_NA_Porcentaje",
            "Prioridad_Territorial"
        ]
    ].head(10)

    print(
        top10.to_string(
            index=False,
            formatters={
                "PIM_Naturaleza_Aventura":
                    lambda x: f"{x:,.0f}",
                "Devengado_Naturaleza_Aventura":
                    lambda x: f"{x:,.0f}",
                "Peso_PIM_NA_Porcentaje":
                    lambda x: f"{x:.1f}%"
            }
        )
    )

    # ------------------------------------------------------
    # RESUMEN NACIONAL
    # ------------------------------------------------------

    resumen_nacional = pd.DataFrame({
        "Indicador": [
            "Registros presupuestales",
            "PIM nacional",
            "Devengado nacional",
            "Registros naturaleza/aventura",
            "PIM naturaleza/aventura",
            "Devengado naturaleza/aventura",
            "Peso PIM naturaleza/aventura"
        ],
        "Valor": [
            len(df),
            pim_total,
            dev_total,
            len(na),
            pim_na,
            dev_na,
            peso_nacional
        ]
    })

    # ------------------------------------------------------
    # GUARDAR
    # ------------------------------------------------------

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        regional.to_excel(
            writer,
            sheet_name="Matriz_Regional",
            index=False
        )

        na.to_excel(
            writer,
            sheet_name="Base_Naturaleza_Aventura",
            index=False
        )

        resumen_nacional.to_excel(
            writer,
            sheet_name="Resumen_Nacional",
            index=False
        )

        top10.to_excel(
            writer,
            sheet_name="Top_10",
            index=False
        )

    print("\n" + "=" * 80)
    print("ARCHIVO GENERADO")
    print("=" * 80)

    print(SALIDA)

    print("\n✓ MATRIZ REGIONAL DEL RADAR COMPLETADA")
    print("FIN")


if __name__ == "__main__":
    main()