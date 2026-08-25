from pathlib import Path
import pandas as pd
import unicodedata
import re

ENTRADA = Path("outputs/radar_turismo_base_maestra_2026.xlsx")
SALIDA = Path("outputs/radar_turismo_clasificacion_refinada_2026.xlsx")

NATURALEZA = [
    "naturaleza", "natural", "bosque", "selva", "amazonia",
    "amazonico", "laguna", "lago", "rio", "catarata",
    "cascada", "humedal", "manglar", "montana", "cordillera",
    "nevado", "glaciar", "canon", "quebrada", "valle",
    "playa", "isla", "reserva", "parque nacional",
    "area natural", "biodiversidad", "fauna", "flora",
    "ecoturismo"
]

AVENTURA = [
    "aventura", "trekking", "senderismo", "caminata", "sendero",
    "montanismo", "andinismo", "escalada", "rapel", "rappel",
    "canotaje", "rafting", "kayak", "ciclismo", "bicicleta",
    "mountain bike", "parapente", "tirolesa", "zipline",
    "surf", "buceo", "snorkel", "cabalgata", "campamento",
    "camping", "sandboard"
]

TURISMO = [
    "turismo", "turistico", "turistica", "turisticos", "turisticas",
    "visitante", "visitantes", "recurso turistico",
    "recursos turisticos", "atractivo turistico",
    "atractivos turisticos", "servicio turistico",
    "servicios turisticos"
]

INFRAESTRUCTURA = [
    "infraestructura turistica", "mirador", "malecon",
    "embarcadero", "muelle", "centro de interpretacion",
    "centro de visitantes", "senalizacion", "parador",
    "refugio", "estacionamiento", "servicios higienicos",
    "acondicionamiento turistico"
]

ACCESO = [
    "acceso", "accesibilidad", "carretera", "camino",
    "trocha", "via", "puente", "transporte", "teleferico"
]


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


def existe_termino(texto, termino):
    """Busca palabras o expresiones completas, evitando falsos positivos."""
    termino = normalizar(termino)

    patron = r"(?<!\w)" + re.escape(termino) + r"(?!\w)"

    return bool(re.search(patron, texto))


def encontrar(texto, diccionario):
    return [
        termino
        for termino in diccionario
        if existe_termino(texto, termino)
    ]


def clasificar(texto):

    nat = encontrar(texto, NATURALEZA)
    ave = encontrar(texto, AVENTURA)
    tur = encontrar(texto, TURISMO)
    infra = encontrar(texto, INFRAESTRUCTURA)
    acceso = encontrar(texto, ACCESO)

    # VINCULACIÓN DIRECTA
    if ave and tur:
        return "DIRECTA"

    if nat and tur:
        return "DIRECTA"

    if ave:
        return "DIRECTA"

    # VINCULACIÓN COMPLEMENTARIA
    if tur and infra:
        return "COMPLEMENTARIA"

    if tur and acceso:
        return "COMPLEMENTARIA"

    if nat and (infra or acceso):
        return "COMPLEMENTARIA"

    # REQUIERE REVISIÓN
    if nat:
        return "NO CONCLUYENTE"

    # TURISMO SIN EVIDENCIA DE NATURALEZA/AVENTURA
    if tur:
        return "TURISMO GENERAL"

    return "NO VINCULADO"


def main():

    print("=" * 90)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("MOTOR SEMÁNTICO REFINADO V2")
    print("=" * 90)

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Base_Maestra"
    )

    print(f"\nRegistros cargados: {len(df):,}")

    df["Texto_Radar"] = (
        df["Proyecto"]
        .fillna("")
        .astype(str)
        .apply(normalizar)
    )

    df["Keywords_Naturaleza"] = df["Texto_Radar"].apply(
        lambda x: ", ".join(encontrar(x, NATURALEZA))
    )

    df["Keywords_Aventura"] = df["Texto_Radar"].apply(
        lambda x: ", ".join(encontrar(x, AVENTURA))
    )

    df["Keywords_Turismo"] = df["Texto_Radar"].apply(
        lambda x: ", ".join(encontrar(x, TURISMO))
    )

    df["Keywords_Infraestructura"] = df["Texto_Radar"].apply(
        lambda x: ", ".join(encontrar(x, INFRAESTRUCTURA))
    )

    df["Keywords_Acceso"] = df["Texto_Radar"].apply(
        lambda x: ", ".join(encontrar(x, ACCESO))
    )

    df["Vinculacion_Radar_V2"] = (
        df["Texto_Radar"].apply(clasificar)
    )

    # --------------------------------------------------------
    # RESUMEN NACIONAL
    # --------------------------------------------------------

    resumen = (
        df.groupby("Vinculacion_Radar_V2", as_index=False)
        .agg(
            Registros=("ID_Radar", "count"),
            PIM=("PIM", "sum"),
            Devengado=("Devengado", "sum")
        )
    )

    pim_total = df["PIM"].sum()

    resumen["Peso_PIM_Porcentaje"] = (
        resumen["PIM"] / pim_total * 100
    )

    # --------------------------------------------------------
    # MATRIZ REGIONAL
    # Solo DIRECTA + COMPLEMENTARIA
    # --------------------------------------------------------

    vinculados = df[
        df["Vinculacion_Radar_V2"].isin(
            ["DIRECTA", "COMPLEMENTARIA"]
        )
    ].copy()

    regional = (
        vinculados
        .groupby("Departamento", as_index=False)
        .agg(
            Registros_Radar=("ID_Radar", "count"),
            PIM_Radar=("PIM", "sum"),
            Devengado_Radar=("Devengado", "sum")
        )
    )

    total_regional = (
        df.groupby("Departamento", as_index=False)
        .agg(
            PIM_Total=("PIM", "sum")
        )
    )

    regional = regional.merge(
        total_regional,
        on="Departamento",
        how="left"
    )

    regional["Peso_Radar_PIM_Porcentaje"] = (
        regional["PIM_Radar"]
        / regional["PIM_Total"]
        * 100
    )

    regional["Avance_Radar_Porcentaje"] = (
        regional["Devengado_Radar"]
        / regional["PIM_Radar"]
        * 100
    ).fillna(0)

    regional = regional.sort_values(
        "PIM_Radar",
        ascending=False
    )

    # --------------------------------------------------------
    # RESULTADOS
    # --------------------------------------------------------

    print("\n" + "=" * 90)
    print("CLASIFICACIÓN NACIONAL V2")
    print("=" * 90)

    print(
        resumen.to_string(
            index=False,
            formatters={
                "PIM": lambda x: f"{x:,.0f}",
                "Devengado": lambda x: f"{x:,.0f}",
                "Peso_PIM_Porcentaje": lambda x: f"{x:.1f}%"
            }
        )
    )

    print("\n" + "=" * 90)
    print("TOP 15 TERRITORIOS - CLASIFICACIÓN V2")
    print("=" * 90)

    print(
        regional.head(15).to_string(
            index=False,
            formatters={
                "PIM_Radar": lambda x: f"{x:,.0f}",
                "Devengado_Radar": lambda x: f"{x:,.0f}",
                "PIM_Total": lambda x: f"{x:,.0f}",
                "Peso_Radar_PIM_Porcentaje": lambda x: f"{x:.1f}%",
                "Avance_Radar_Porcentaje": lambda x: f"{x:.1f}%"
            }
        )
    )

    # --------------------------------------------------------
    # AUDITORÍA
    # --------------------------------------------------------

    revisar = df[
        df["Vinculacion_Radar_V2"].isin(
            ["DIRECTA", "COMPLEMENTARIA", "NO CONCLUYENTE"]
        )
    ].copy()

    revisar = revisar.sort_values(
        "PIM",
        ascending=False
    )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Base_Clasificada_V2",
            index=False
        )

        resumen.to_excel(
            writer,
            sheet_name="Resumen_Nacional",
            index=False
        )

        regional.to_excel(
            writer,
            sheet_name="Matriz_Regional_V2",
            index=False
        )

        revisar.to_excel(
            writer,
            sheet_name="Auditoria",
            index=False
        )

    print("\n" + "=" * 90)
    print("CONTROL PRESUPUESTAL")
    print("=" * 90)

    print(f"PIM TOTAL       : S/ {df['PIM'].sum():,.0f}")
    print(f"DEVENGADO TOTAL : S/ {df['Devengado'].sum():,.0f}")

    print("\nARCHIVO GENERADO:")
    print(SALIDA)

    print("\n✓ MOTOR SEMÁNTICO V2 COMPLETADO")
    print("FIN")


if __name__ == "__main__":
    main()