from pathlib import Path
import pandas as pd
import unicodedata
import re

ENTRADA = Path("outputs/radar_turismo_base_maestra_2026.xlsx")
SALIDA = Path("outputs/radar_turismo_auditoria_clasificacion_2026.xlsx")

TOP_DEPARTAMENTOS = [
    "AMAZONAS",
    "LORETO",
    "ANCASH",
    "PUNO",
    "HUANUCO",
    "AREQUIPA",
    "UCAYALI",
    "CUSCO",
    "TACNA",
    "LIMA",
]

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

PALABRAS_TURISMO = [
    "turismo",
    "turistico",
    "turistica",
    "visitante",
    "visitantes",
    "recurso turistico",
    "atractivo turistico",
    "servicios turisticos",
]

PALABRAS_INFRAESTRUCTURA = [
    "infraestructura",
    "mirador",
    "malecon",
    "embarcadero",
    "muelle",
    "centro de interpretacion",
    "centro de visitantes",
    "senalizacion",
    "parador",
    "refugio",
    "estacionamiento",
    "servicios higienicos",
    "acondicionamiento",
]

PALABRAS_ACCESO = [
    "acceso",
    "accesibilidad",
    "carretera",
    "camino",
    "trocha",
    "via",
    "puente",
    "transporte",
    "teleferico",
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


def coincidencias(texto, palabras):
    return [
        palabra
        for palabra in palabras
        if palabra in texto
    ]


def clasificar_vinculacion(texto):

    nat = coincidencias(texto, PALABRAS_NATURALEZA)
    ave = coincidencias(texto, PALABRAS_AVENTURA)
    tur = coincidencias(texto, PALABRAS_TURISMO)
    inf = coincidencias(texto, PALABRAS_INFRAESTRUCTURA)
    acc = coincidencias(texto, PALABRAS_ACCESO)

    # --------------------------------------------------
    # VINCULACIÓN DIRECTA
    # --------------------------------------------------

    if ave:
        return "DIRECTA"

    if nat and tur:
        return "DIRECTA"

    if len(nat) >= 2:
        return "DIRECTA"

    # --------------------------------------------------
    # VINCULACIÓN COMPLEMENTARIA
    # --------------------------------------------------

    if nat and (inf or acc):
        return "COMPLEMENTARIA"

    if tur and (inf or acc):
        return "COMPLEMENTARIA"

    # --------------------------------------------------
    # NO CONCLUYENTE
    # --------------------------------------------------

    if nat:
        return "NO CONCLUYENTE"

    return "NO VINCULADO"


def main():

    print("=" * 90)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("AUDITORÍA DE CLASIFICACIÓN")
    print("=" * 90)

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Base_Maestra"
    )

    print(f"\nRegistros cargados: {len(df):,}")

    df["Texto_Normalizado"] = (
        df["Proyecto"]
        .fillna("")
        .astype(str)
        .apply(normalizar)
    )

    df["Palabras_Naturaleza"] = (
        df["Texto_Normalizado"]
        .apply(
            lambda x: ", ".join(
                coincidencias(
                    x,
                    PALABRAS_NATURALEZA
                )
            )
        )
    )

    df["Palabras_Aventura"] = (
        df["Texto_Normalizado"]
        .apply(
            lambda x: ", ".join(
                coincidencias(
                    x,
                    PALABRAS_AVENTURA
                )
            )
        )
    )

    df["Palabras_Turismo"] = (
        df["Texto_Normalizado"]
        .apply(
            lambda x: ", ".join(
                coincidencias(
                    x,
                    PALABRAS_TURISMO
                )
            )
        )
    )

    df["Palabras_Infraestructura"] = (
        df["Texto_Normalizado"]
        .apply(
            lambda x: ", ".join(
                coincidencias(
                    x,
                    PALABRAS_INFRAESTRUCTURA
                )
            )
        )
    )

    df["Palabras_Acceso"] = (
        df["Texto_Normalizado"]
        .apply(
            lambda x: ", ".join(
                coincidencias(
                    x,
                    PALABRAS_ACCESO
                )
            )
        )
    )

    df["Vinculacion_Radar"] = (
        df["Texto_Normalizado"]
        .apply(clasificar_vinculacion)
    )

    # --------------------------------------------------
    # AUDITORÍA DE TOP 10
    # --------------------------------------------------

    auditoria = df[
        df["Departamento"].isin(TOP_DEPARTAMENTOS)
    ].copy()

    auditoria = auditoria[
        auditoria["Vinculacion_Radar"]
        != "NO VINCULADO"
    ]

    auditoria = auditoria.sort_values(
        [
            "Departamento",
            "PIM"
        ],
        ascending=[
            True,
            False
        ]
    )

    # --------------------------------------------------
    # RESUMEN POR DEPARTAMENTO
    # --------------------------------------------------

    resumen = (
        auditoria
        .groupby(
            [
                "Departamento",
                "Vinculacion_Radar"
            ],
            as_index=False
        )
        .agg(
            Registros=("ID_Radar", "count"),
            PIM=("PIM", "sum"),
            Devengado=("Devengado", "sum"),
        )
    )

    # --------------------------------------------------
    # RESUMEN NACIONAL DE CLASIFICACIÓN
    # --------------------------------------------------

    resumen_nacional = (
        df.groupby(
            "Vinculacion_Radar",
            as_index=False
        )
        .agg(
            Registros=("ID_Radar", "count"),
            PIM=("PIM", "sum"),
            Devengado=("Devengado", "sum"),
        )
    )

    pim_total = df["PIM"].sum()

    resumen_nacional["Peso_PIM_Porcentaje"] = (
        resumen_nacional["PIM"]
        / pim_total
        * 100
    )

    print("\n" + "=" * 90)
    print("CLASIFICACIÓN NACIONAL REFINADA")
    print("=" * 90)

    print(
        resumen_nacional.to_string(
            index=False,
            formatters={
                "PIM": lambda x: f"{x:,.0f}",
                "Devengado": lambda x: f"{x:,.0f}",
                "Peso_PIM_Porcentaje":
                    lambda x: f"{x:.1f}%"
            }
        )
    )

    # --------------------------------------------------
    # TOP PROYECTOS PARA AUDITORÍA VISUAL
    # --------------------------------------------------

    top_auditoria = (
        auditoria[
            [
                "Departamento",
                "Codigo_Proyecto",
                "Proyecto",
                "Vinculacion_Radar",
                "PIM",
                "Devengado",
                "Palabras_Naturaleza",
                "Palabras_Aventura",
                "Palabras_Turismo",
                "Palabras_Infraestructura",
                "Palabras_Acceso",
            ]
        ]
        .sort_values(
            "PIM",
            ascending=False
        )
        .head(50)
    )

    print("\n" + "=" * 90)
    print("TOP 50 REGISTROS PARA AUDITORÍA")
    print("=" * 90)

    print(
        top_auditoria.to_string(
            index=False,
            formatters={
                "PIM": lambda x: f"{x:,.0f}",
                "Devengado": lambda x: f"{x:,.0f}",
            }
        )
    )

    # --------------------------------------------------
    # GUARDAR EXCEL
    # --------------------------------------------------

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        auditoria.to_excel(
            writer,
            sheet_name="Auditoria_Top10",
            index=False
        )

        resumen.to_excel(
            writer,
            sheet_name="Resumen_Departamento",
            index=False
        )

        resumen_nacional.to_excel(
            writer,
            sheet_name="Resumen_Nacional",
            index=False
        )

        top_auditoria.to_excel(
            writer,
            sheet_name="Top_50_Auditoria",
            index=False
        )

    print("\n" + "=" * 90)
    print("ARCHIVO GENERADO")
    print("=" * 90)

    print(SALIDA)

    print("\n✓ AUDITORÍA DE CLASIFICACIÓN COMPLETADA")
    print("FIN")


if __name__ == "__main__":
    main()