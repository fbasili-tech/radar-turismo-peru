from pathlib import Path
import pandas as pd
import unicodedata
import re

# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 11: ENRIQUECIMIENTO DE RECURSOS Y DESTINOS
# ============================================================

ENTRADA = Path(
    "outputs/radar_turismo_potencial_aventura_2026.xlsx"
)

SALIDA = Path(
    "outputs/radar_turismo_destinos_enriquecidos_2026.xlsx"
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
# TÉRMINOS TERRITORIALES
# ============================================================

TIPOS_RECURSO = {

    "LAGUNA": [
        "laguna",
        "lagunas"
    ],

    "LAGO": [
        "lago",
        "lagos"
    ],

    "RIO": [
        "rio",
        "rios"
    ],

    "CATARATA": [
        "catarata",
        "cataratas"
    ],

    "CASCADA": [
        "cascada",
        "cascadas"
    ],

    "PLAYA": [
        "playa",
        "playas"
    ],

    "BOSQUE": [
        "bosque",
        "bosques"
    ],

    "VALLE": [
        "valle",
        "valles"
    ],

    "CANON": [
        "canon",
        "canones"
    ],

    "MONTANA": [
        "montana",
        "montanas"
    ],

    "NEVADO": [
        "nevado",
        "nevados"
    ],

    "CORDILLERA": [
        "cordillera",
        "cordilleras"
    ],

    "MIRADOR": [
        "mirador",
        "miradores"
    ],

    "SENDERO": [
        "sendero",
        "senderos"
    ],

    "RUTA": [
        "ruta",
        "rutas"
    ],

    "CIRCUITO": [
        "circuito",
        "circuitos"
    ],

    "CAMINO": [
        "camino",
        "caminos"
    ],

    "PARQUE_NACIONAL": [
        "parque nacional"
    ],

    "RESERVA": [
        "reserva nacional",
        "reserva natural",
        "reserva"
    ],

    "SANTUARIO": [
        "santuario nacional",
        "santuario historico",
        "santuario"
    ],

    "COMPLEJO_TURISTICO": [
        "complejo turistico"
    ],

    "RECURSO_TURISTICO": [
        "recurso turistico",
        "recursos turisticos"
    ],

    "ATRACTIVO_TURISTICO": [
        "atractivo turistico",
        "atractivos turisticos"
    ]
}


# ============================================================
# DETECCIÓN DE TIPO DE RECURSO
# ============================================================

def contiene_termino(texto, termino):

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


def detectar_tipos_recurso(texto):

    encontrados = []

    for categoria, palabras in TIPOS_RECURSO.items():

        for palabra in palabras:

            if contiene_termino(
                texto,
                palabra
            ):

                encontrados.append(
                    categoria
                )

                break

    return sorted(
        set(encontrados)
    )


# ============================================================
# EXTRACCIÓN DE NOMBRES DE RECURSO
# ============================================================

PATRONES_RECURSO = [

    r"\blaguna\s+([a-z0-9\s\-]+?)(?=\s+del\s+|\s+de\s+la\s+|\s+en\s+|\s+distrito\s+|\s+provincia\s+|\s+departamento\s+|$)",

    r"\blago\s+([a-z0-9\s\-]+?)(?=\s+del\s+|\s+de\s+la\s+|\s+en\s+|\s+distrito\s+|\s+provincia\s+|\s+departamento\s+|$)",

    r"\bcatarata\s+([a-z0-9\s\-]+?)(?=\s+del\s+|\s+de\s+la\s+|\s+en\s+|\s+distrito\s+|\s+provincia\s+|\s+departamento\s+|$)",

    r"\bplaya\s+([a-z0-9\s\-]+?)(?=\s+del\s+|\s+de\s+la\s+|\s+en\s+|\s+distrito\s+|\s+provincia\s+|\s+departamento\s+|$)",

    r"\bmirador\s+([a-z0-9\s\-]+?)(?=\s+del\s+|\s+de\s+la\s+|\s+en\s+|\s+distrito\s+|\s+provincia\s+|\s+departamento\s+|$)",

    r"\bruta\s+([a-z0-9\s\-]+?)(?=\s+del\s+|\s+de\s+la\s+|\s+en\s+|\s+distrito\s+|\s+provincia\s+|\s+departamento\s+|$)",

    r"\bcircuito\s+([a-z0-9\s\-]+?)(?=\s+del\s+|\s+de\s+la\s+|\s+en\s+|\s+distrito\s+|\s+provincia\s+|\s+departamento\s+|$)",

    r"\bcamino\s+([a-z0-9\s\-]+?)(?=\s+del\s+|\s+de\s+la\s+|\s+en\s+|\s+distrito\s+|\s+provincia\s+|\s+departamento\s+|$)",

    r"\bvalle\s+([a-z0-9\s\-]+?)(?=\s+del\s+|\s+de\s+la\s+|\s+en\s+|\s+distrito\s+|\s+provincia\s+|\s+departamento\s+|$)",

    r"\bnevado\s+([a-z0-9\s\-]+?)(?=\s+del\s+|\s+de\s+la\s+|\s+en\s+|\s+distrito\s+|\s+provincia\s+|\s+departamento\s+|$)",
]


def limpiar_nombre_recurso(nombre):

    nombre = re.sub(
        r"\s+",
        " ",
        nombre
    ).strip()

    palabras_corte = [
        "servicio",
        "servicios",
        "turistico",
        "turisticos",
        "publicos",
        "distrito",
        "provincia",
        "departamento",
        "region"
    ]

    tokens = nombre.split()

    limpio = []

    for token in tokens:

        if token in palabras_corte:
            break

        limpio.append(token)

    nombre = " ".join(limpio)

    return nombre.strip()


def extraer_nombres_recurso(texto):

    encontrados = []

    for patron in PATRONES_RECURSO:

        coincidencias = re.findall(
            patron,
            texto
        )

        for resultado in coincidencias:

            resultado = limpiar_nombre_recurso(
                resultado
            )

            if (
                resultado
                and len(resultado) >= 3
            ):

                encontrados.append(
                    resultado
                )

    return sorted(
        set(encontrados)
    )


# ============================================================
# IDENTIFICACIÓN DE ÁMBITO TURÍSTICO
# ============================================================

def detectar_ambito(row):

    ecosistemas = str(
        row.get(
            "Ecosistemas",
            ""
        )
    )

    proyecto = normalizar(
        row.get(
            "Proyecto",
            ""
        )
    )

    if (
        "MONTANA" in ecosistemas
        or contiene_termino(
            proyecto,
            "nevado"
        )
        or contiene_termino(
            proyecto,
            "cordillera"
        )
    ):
        return "ANDINO / MONTAÑA"

    if (
        "BOSQUE_SELVA" in ecosistemas
        or contiene_termino(
            proyecto,
            "selva"
        )
        or contiene_termino(
            proyecto,
            "bosque"
        )
    ):
        return "AMAZÓNICO / BOSQUE"

    if (
        "MARINO_COSTERO" in ecosistemas
        or contiene_termino(
            proyecto,
            "playa"
        )
    ):
        return "MARINO / COSTERO"

    if (
        "LACUSTRE" in ecosistemas
        or "FLUVIAL" in ecosistemas
    ):
        return "LACUSTRE / FLUVIAL"

    if (
        "AREAS_NATURALES"
        in ecosistemas
    ):
        return "ÁREA NATURAL"

    if (
        "VALLE_PAISAJE"
        in ecosistemas
    ):
        return "VALLE / PAISAJE"

    return "OTRO / NO DETERMINADO"


# ============================================================
# NIVEL DE INFORMACIÓN TERRITORIAL
# ============================================================

def calidad_evidencia(row):

    tipos = row[
        "Tipos_Recurso"
    ]

    nombres = row[
        "Recursos_Extraidos"
    ]

    if tipos and nombres:
        return "ALTA"

    if tipos:
        return "MEDIA"

    return "BAJA"


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():

    print("=" * 100)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("ENRIQUECIMIENTO DE RECURSOS Y DESTINOS")
    print("=" * 100)

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Base_Potencial"
    )

    print(
        f"\nRegistros cargados: "
        f"{len(df):,}"
    )

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    df["Texto_Destino"] = (
        df["Proyecto"]
        .fillna("")
        .astype(str)
        .apply(normalizar)
    )

    # --------------------------------------------------------
    # TIPO DE RECURSO
    # --------------------------------------------------------

    df["Tipos_Recurso"] = (
        df["Texto_Destino"]
        .apply(
            detectar_tipos_recurso
        )
    )

    # --------------------------------------------------------
    # RECURSOS EXTRAÍDOS
    # --------------------------------------------------------

    df["Recursos_Extraidos"] = (
        df["Texto_Destino"]
        .apply(
            extraer_nombres_recurso
        )
    )

    # --------------------------------------------------------
    # ÁMBITO TURÍSTICO
    # --------------------------------------------------------

    df["Ambito_Turistico"] = (
        df.apply(
            detectar_ambito,
            axis=1
        )
    )

    # --------------------------------------------------------
    # CALIDAD DE EVIDENCIA
    # --------------------------------------------------------

    df["Calidad_Evidencia_Territorial"] = (
        df.apply(
            calidad_evidencia,
            axis=1
        )
    )

    # --------------------------------------------------------
    # CONVERTIR LISTAS EN TEXTO
    # --------------------------------------------------------

    df["Tipos_Recurso"] = (
        df["Tipos_Recurso"]
        .apply(
            lambda x:
            ", ".join(x)
        )
    )

    df["Recursos_Extraidos"] = (
        df["Recursos_Extraidos"]
        .apply(
            lambda x:
            ", ".join(x)
        )
    )

    # ========================================================
    # RESUMEN POR ÁMBITO
    # ========================================================

    resumen_ambito = (
        df.groupby(
            "Ambito_Turistico",
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

    pim_total = df["PIM"].sum()

    resumen_ambito[
        "Peso_PIM_Radar"
    ] = (
        resumen_ambito["PIM"]
        / pim_total
        * 100
    )

    resumen_ambito[
        "Avance_Porcentaje"
    ] = (
        resumen_ambito["Devengado"]
        / resumen_ambito["PIM"]
        * 100
    ).fillna(0)

    resumen_ambito = (
        resumen_ambito
        .sort_values(
            "PIM",
            ascending=False
        )
    )

    # ========================================================
    # RESUMEN DE CALIDAD TERRITORIAL
    # ========================================================

    resumen_calidad = (
        df.groupby(
            "Calidad_Evidencia_Territorial",
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
            )
        )
    )

    resumen_calidad[
        "Peso_PIM_Radar"
    ] = (
        resumen_calidad["PIM"]
        / pim_total
        * 100
    )

    # ========================================================
    # TOP RECURSOS IDENTIFICADOS
    # ========================================================

    recursos = df[
        df["Recursos_Extraidos"]
        != ""
    ].copy()

    recursos = recursos[
        [
            "Departamento",
            "Codigo_Proyecto",
            "Proyecto",
            "Tipos_Recurso",
            "Recursos_Extraidos",
            "Ambito_Turistico",
            "Nivel_Evidencia_Aventura",
            "PIM",
            "Devengado"
        ]
    ]

    recursos = recursos.sort_values(
        "PIM",
        ascending=False
    )

    # ========================================================
    # MOSTRAR RESULTADOS
    # ========================================================

    print("\n" + "=" * 100)
    print("ÁMBITOS TURÍSTICOS")
    print("=" * 100)

    print(
        resumen_ambito.to_string(
            index=False,
            formatters={
                "PIM":
                    lambda x:
                    f"{x:,.0f}",

                "Devengado":
                    lambda x:
                    f"{x:,.0f}",

                "Peso_PIM_Radar":
                    lambda x:
                    f"{x:.1f}%",

                "Avance_Porcentaje":
                    lambda x:
                    f"{x:.1f}%"
            }
        )
    )

    print("\n" + "=" * 100)
    print("CALIDAD DE EVIDENCIA TERRITORIAL")
    print("=" * 100)

    print(
        resumen_calidad.to_string(
            index=False,
            formatters={
                "PIM":
                    lambda x:
                    f"{x:,.0f}",

                "Peso_PIM_Radar":
                    lambda x:
                    f"{x:.1f}%"
            }
        )
    )

    print("\n" + "=" * 100)
    print("TOP 20 RECURSOS / DESTINOS IDENTIFICADOS")
    print("=" * 100)

    print(
        recursos.head(20).to_string(
            index=False,
            formatters={
                "PIM":
                    lambda x:
                    f"{x:,.0f}",

                "Devengado":
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
        f"REGISTROS RADAR : "
        f"{len(df):,}"
    )

    print(
        f"PIM RADAR       : "
        f"S/ {df['PIM'].sum():,.0f}"
    )

    print(
        f"DEVENGADO RADAR : "
        f"S/ {df['Devengado'].sum():,.0f}"
    )

    print(
        f"RECURSOS CON NOMBRE EXTRAÍDO : "
        f"{len(recursos):,}"
    )

    # ========================================================
    # EXPORTAR
    # ========================================================

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Base_Destinos",
            index=False
        )

        resumen_ambito.to_excel(
            writer,
            sheet_name="Ambitos_Turisticos",
            index=False
        )

        resumen_calidad.to_excel(
            writer,
            sheet_name="Calidad_Evidencia",
            index=False
        )

        recursos.to_excel(
            writer,
            sheet_name="Recursos_Identificados",
            index=False
        )

    print("\nARCHIVO GENERADO:")
    print(SALIDA)

    print(
        "\n✓ ENRIQUECIMIENTO TERRITORIAL COMPLETADO"
    )

    print("FIN")


if __name__ == "__main__":
    main()