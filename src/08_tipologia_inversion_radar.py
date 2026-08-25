from pathlib import Path
import pandas as pd
import unicodedata
import re

# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 08: TIPOLOGÍA DE LA INVERSIÓN
# ============================================================

ENTRADA = Path(
    "outputs/radar_turismo_clasificacion_refinada_2026.xlsx"
)

SALIDA = Path(
    "outputs/radar_turismo_tipologia_inversion_2026.xlsx"
)


# ============================================================
# NORMALIZACIÓN
# ============================================================

def normalizar(texto):

    if pd.isna(texto):
        return ""

    texto = str(texto).lower()

    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    texto = re.sub(
        r"[^a-z0-9\s]",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ============================================================
# BÚSQUEDA DE TÉRMINOS COMPLETOS
# ============================================================

def contiene(texto, termino):

    termino = normalizar(termino)

    patron = (
        r"(?<!\w)"
        + re.escape(termino)
        + r"(?!\w)"
    )

    return bool(
        re.search(
            patron,
            texto
        )
    )


def contiene_alguno(texto, terminos):

    return any(
        contiene(texto, termino)
        for termino in terminos
    )


# ============================================================
# DICCIONARIOS DE TIPOLOGÍAS
# ============================================================

TIPOLOGIAS = {

    "AVENTURA": [
        "aventura",
        "trekking",
        "senderismo",
        "caminata",
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
        "parapente",
        "tirolesa",
        "zipline",
        "surf",
        "buceo",
        "snorkel",
        "cabalgata",
        "sandboard"
    ],

    "SENDEROS_Y_RUTAS": [
        "sendero",
        "senderos",
        "ruta",
        "rutas",
        "circuito",
        "circuitos",
        "camino",
        "caminos"
    ],

    "MONTANA_Y_ALTA_MONTANA": [
        "montana",
        "montanas",
        "cordillera",
        "nevado",
        "nevados",
        "glaciar",
        "glaciares",
        "andinismo",
        "montanismo"
    ],

    "LACUSTRE_FLUVIAL": [
        "lago",
        "laguna",
        "lagunas",
        "rio",
        "rios",
        "catarata",
        "cataratas",
        "cascada",
        "cascadas",
        "humedal",
        "humedales"
    ],

    "MARINO_COSTERO": [
        "playa",
        "playas",
        "mar",
        "marino",
        "marina",
        "isla",
        "islas",
        "bahia",
        "litoral",
        "costa"
    ],

    "BOSQUES_Y_BIODIVERSIDAD": [
        "bosque",
        "bosques",
        "selva",
        "amazonia",
        "amazonico",
        "biodiversidad",
        "flora",
        "fauna",
        "ecoturismo"
    ],

    "AREAS_NATURALES": [
        "area natural",
        "areas naturales",
        "parque nacional",
        "reserva nacional",
        "reserva natural",
        "santuario nacional",
        "santuario historico",
        "area protegida"
    ],

    "MIRADORES_Y_OBSERVACION": [
        "mirador",
        "miradores",
        "observacion",
        "avistamiento"
    ],

    "EMBARCADEROS_Y_MUELLES": [
        "embarcadero",
        "embarcaderos",
        "muelle",
        "muelles",
        "marina turistica"
    ],

    "INTERPRETACION": [
        "centro de interpretacion",
        "interpretacion",
        "centro de visitantes",
        "informacion turistica"
    ],

    "ACCESIBILIDAD": [
        "acceso",
        "accesibilidad",
        "carretera",
        "trocha",
        "via",
        "vias",
        "puente",
        "teleferico"
    ],

    "INFRAESTRUCTURA_TURISTICA": [
        "infraestructura turistica",
        "acondicionamiento turistico",
        "servicios turisticos",
        "servicio turistico",
        "instalacion turistica",
        "instalaciones turisticas",
        "senalizacion",
        "servicios higienicos",
        "estacionamiento"
    ],

    "RECREACION": [
        "recreacion",
        "recreativo",
        "recreativa",
        "espacio publico",
        "espacios publicos"
    ]
}


# ============================================================
# DETECTAR TIPOLOGÍAS
# ============================================================

def detectar_tipologias(texto):

    encontradas = []

    for tipologia, palabras in TIPOLOGIAS.items():

        if contiene_alguno(
            texto,
            palabras
        ):

            encontradas.append(
                tipologia
            )

    return encontradas


# ============================================================
# TIPOLOGÍA PRINCIPAL
# ============================================================

PRIORIDAD_TIPOLOGIA = [

    "AVENTURA",

    "MONTANA_Y_ALTA_MONTANA",

    "AREAS_NATURALES",

    "BOSQUES_Y_BIODIVERSIDAD",

    "LACUSTRE_FLUVIAL",

    "MARINO_COSTERO",

    "SENDEROS_Y_RUTAS",

    "MIRADORES_Y_OBSERVACION",

    "EMBARCADEROS_Y_MUELLES",

    "INTERPRETACION",

    "ACCESIBILIDAD",

    "INFRAESTRUCTURA_TURISTICA",

    "RECREACION"
]


def tipologia_principal(tipologias):

    if not tipologias:
        return "OTROS"

    for categoria in PRIORIDAD_TIPOLOGIA:

        if categoria in tipologias:
            return categoria

    return tipologias[0]


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():

    print("=" * 90)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("TIPOLOGÍA DE INVERSIÓN")
    print("=" * 90)

    # --------------------------------------------------------
    # CARGAR BASE V2
    # --------------------------------------------------------

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Base_Clasificada_V2"
    )

    print(
        f"\nRegistros cargados: {len(df):,}"
    )

    # --------------------------------------------------------
    # SOLO NÚCLEO RADAR
    # --------------------------------------------------------

    radar = df[
        df["Vinculacion_Radar_V2"]
        .isin(
            [
                "DIRECTA",
                "COMPLEMENTARIA"
            ]
        )
    ].copy()

    print(
        f"Registros DIRECTOS + COMPLEMENTARIOS: "
        f"{len(radar):,}"
    )

    # --------------------------------------------------------
    # NORMALIZAR
    # --------------------------------------------------------

    radar["Texto_Tipologia"] = (
        radar["Proyecto"]
        .fillna("")
        .astype(str)
        .apply(normalizar)
    )

    # --------------------------------------------------------
    # DETECTAR TIPOLOGÍAS
    # --------------------------------------------------------

    radar["Tipologias_Detectadas"] = (
        radar["Texto_Tipologia"]
        .apply(detectar_tipologias)
    )

    radar["Tipologia_Principal"] = (
        radar["Tipologias_Detectadas"]
        .apply(tipologia_principal)
    )

    radar["Tipologias_Detectadas"] = (
        radar["Tipologias_Detectadas"]
        .apply(
            lambda x:
            ", ".join(x)
        )
    )

    # --------------------------------------------------------
    # RESUMEN POR TIPOLOGÍA
    # --------------------------------------------------------

    resumen = (
        radar
        .groupby(
            "Tipologia_Principal",
            as_index=False
        )
        .agg(
            Registros=(
                "ID_Radar",
                "count"
            ),
            PIM=(
                "PIM",
                "sum"
            ),
            Devengado=(
                "Devengado",
                "sum"
            )
        )
    )

    pim_radar = radar["PIM"].sum()

    resumen["Peso_PIM_Radar_Porcentaje"] = (
        resumen["PIM"]
        / pim_radar
        * 100
    )

    resumen["Avance_Porcentaje"] = (
        resumen["Devengado"]
        / resumen["PIM"]
        * 100
    ).fillna(0)

    resumen = resumen.sort_values(
        "PIM",
        ascending=False
    )

    # --------------------------------------------------------
    # MATRIZ DEPARTAMENTO + TIPOLOGÍA
    # --------------------------------------------------------

    regional = (
        radar
        .groupby(
            [
                "Departamento",
                "Tipologia_Principal"
            ],
            as_index=False
        )
        .agg(
            Registros=(
                "ID_Radar",
                "count"
            ),
            PIM=(
                "PIM",
                "sum"
            ),
            Devengado=(
                "Devengado",
                "sum"
            )
        )
    )

    regional["Avance_Porcentaje"] = (
        regional["Devengado"]
        / regional["PIM"]
        * 100
    ).fillna(0)

    regional = regional.sort_values(
        [
            "Departamento",
            "PIM"
        ],
        ascending=[
            True,
            False
        ]
    )

    # --------------------------------------------------------
    # TOP DE PROYECTOS
    # --------------------------------------------------------

    top_proyectos = radar[
        [
            "Departamento",
            "Codigo_Proyecto",
            "Proyecto",
            "Vinculacion_Radar_V2",
            "Tipologia_Principal",
            "Tipologias_Detectadas",
            "PIM",
            "Devengado"
        ]
    ].copy()

    top_proyectos = (
        top_proyectos
        .sort_values(
            "PIM",
            ascending=False
        )
    )

    # --------------------------------------------------------
    # MOSTRAR RESUMEN
    # --------------------------------------------------------

    print("\n" + "=" * 90)
    print("INVERSIÓN POR TIPOLOGÍA")
    print("=" * 90)

    print(
        resumen.to_string(
            index=False,
            formatters={
                "PIM":
                    lambda x: f"{x:,.0f}",

                "Devengado":
                    lambda x: f"{x:,.0f}",

                "Peso_PIM_Radar_Porcentaje":
                    lambda x: f"{x:.1f}%",

                "Avance_Porcentaje":
                    lambda x: f"{x:.1f}%"
            }
        )
    )

    # --------------------------------------------------------
    # TOP 20 PROYECTOS
    # --------------------------------------------------------

    print("\n" + "=" * 90)
    print("TOP 20 PROYECTOS DEL NÚCLEO RADAR")
    print("=" * 90)

    print(
        top_proyectos
        .head(20)
        .to_string(
            index=False,
            formatters={
                "PIM":
                    lambda x: f"{x:,.0f}",

                "Devengado":
                    lambda x: f"{x:,.0f}"
            }
        )
    )

    # --------------------------------------------------------
    # CONTROL
    # --------------------------------------------------------

    pim_total = df["PIM"].sum()
    dev_total = df["Devengado"].sum()

    dev_radar = radar["Devengado"].sum()

    peso_radar = (
        pim_radar
        / pim_total
        * 100
    )

    print("\n" + "=" * 90)
    print("CONTROL")
    print("=" * 90)

    print(
        f"PIM BASE NACIONAL : "
        f"S/ {pim_total:,.0f}"
    )

    print(
        f"PIM NÚCLEO RADAR  : "
        f"S/ {pim_radar:,.0f}"
    )

    print(
        f"PESO NÚCLEO RADAR : "
        f"{peso_radar:.1f}%"
    )

    print(
        f"DEVENGADO RADAR   : "
        f"S/ {dev_radar:,.0f}"
    )

    print(
        f"DEVENGADO NACIONAL: "
        f"S/ {dev_total:,.0f}"
    )

    # --------------------------------------------------------
    # GUARDAR EXCEL
    # --------------------------------------------------------

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        radar.to_excel(
            writer,
            sheet_name="Base_Tipologias",
            index=False
        )

        resumen.to_excel(
            writer,
            sheet_name="Resumen_Tipologias",
            index=False
        )

        regional.to_excel(
            writer,
            sheet_name="Matriz_Regional_Tipologia",
            index=False
        )

        top_proyectos.to_excel(
            writer,
            sheet_name="Ranking_Proyectos",
            index=False
        )

    print("\nARCHIVO GENERADO:")
    print(SALIDA)

    print(
        "\n✓ TIPOLOGÍA DE INVERSIÓN COMPLETADA"
    )

    print("FIN")


if __name__ == "__main__":
    main()