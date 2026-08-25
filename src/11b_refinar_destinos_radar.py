from pathlib import Path
import pandas as pd
import unicodedata
import re

# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 11B: REFINAMIENTO TERRITORIAL Y VOCACIÓN N/A
# ============================================================

ENTRADA = Path(
    "outputs/radar_turismo_destinos_enriquecidos_2026.xlsx"
)

SALIDA = Path(
    "outputs/radar_turismo_destinos_refinados_2026.xlsx"
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

    texto = re.sub(r"[^a-z0-9\s\-]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def contiene(texto, termino):
    termino = normalizar(termino)

    patron = (
        r"(?<!\w)"
        + re.escape(termino)
        + r"(?!\w)"
    )

    return bool(re.search(patron, texto))


def contiene_alguno(texto, terminos):
    return any(
        contiene(texto, termino)
        for termino in terminos
    )


# ============================================================
# DICCIONARIOS TERRITORIALES
# ============================================================

NATURALEZA_ALTA = [
    "laguna",
    "lago",
    "rio",
    "catarata",
    "cascada",
    "canon",
    "quebrada",
    "montana",
    "cordillera",
    "nevado",
    "glaciar",
    "bosque",
    "selva",
    "biodiversidad",
    "parque nacional",
    "reserva nacional",
    "area natural",
    "santuario nacional"
]

RUTAS_NA = [
    "camino inca",
    "qhapac nan",
    "qhapaq nan",
    "sendero",
    "ruta",
    "circuito",
    "camino"
]

MARINO_COSTERO = [
    "playa",
    "mar",
    "marino",
    "bahia",
    "litoral",
    "costa"
]

PAISAJE = [
    "valle",
    "paisaje",
    "paisajistico",
    "mirador"
]

TURISMO = [
    "turismo",
    "turistico",
    "turistica",
    "turisticos",
    "turisticas",
    "recurso turistico",
    "recursos turisticos",
    "atractivo turistico",
    "servicios turisticos"
]

INFRAESTRUCTURA = [
    "acceso",
    "accesibilidad",
    "sendero",
    "camino",
    "ruta",
    "circuito",
    "mirador",
    "embarcadero",
    "muelle",
    "centro de interpretacion",
    "acondicionamiento turistico"
]


# ============================================================
# EXTRACCIÓN DE RECURSOS
# ============================================================

PATRONES = [
    ("LAGUNA", r"\blaguna\s+(?:de\s+)?([a-z0-9\- ]+?)(?=\s+en\s+|\s+del\s+distrito|\s+distrito|\s+provincia|\s+departamento|$)"),
    ("LAGO", r"\blago\s+(?:de\s+)?([a-z0-9\- ]+?)(?=\s+en\s+|\s+del\s+distrito|\s+distrito|\s+provincia|\s+departamento|$)"),
    ("CATARATA", r"\bcatarata\s+(?:de\s+)?([a-z0-9\- ]+?)(?=\s+en\s+|\s+del\s+distrito|\s+distrito|\s+provincia|\s+departamento|$)"),
    ("CASCADA", r"\bcascada\s+(?:de\s+)?([a-z0-9\- ]+?)(?=\s+en\s+|\s+del\s+distrito|\s+distrito|\s+provincia|\s+departamento|$)"),
    ("PLAYA", r"\bplaya\s+(?:de\s+)?([a-z0-9\- ]+?)(?=\s+en\s+|\s+del\s+distrito|\s+distrito|\s+provincia|\s+departamento|$)"),
    ("VALLE", r"\bvalle\s+(?:del\s+|de\s+)?([a-z0-9\- ]+?)(?=\s+en\s+|\s+sector|\s+distrito|\s+provincia|\s+region|$)"),
    ("MIRADOR", r"\bmirador\s+(?:natural\s+)?([a-z0-9\- ]+?)(?=\s+y\s+vias|\s+del\s+distrito|\s+distrito|\s+provincia|\s+departamento|$)"),
    ("CANON", r"\bcanon\s+(?:del\s+|de\s+)?([a-z0-9\- ]+?)(?=\s+en\s+|\s+distrito|\s+provincia|\s+departamento|$)"),
    ("CAMINO_INCA", r"\bcamino\s+inca\s+([a-z0-9\- ]+?)(?=\s+en\s+|\s+del\s+caserio|\s+distrito|\s+provincia|\s+region|$)"),
    ("QHAPAQ_NAN", r"\bqh?apaq\s+nan\s+([a-z0-9\- ]+?)(?=\s+distrito|\s+distritos|\s+provincia|\s+region|$)"),
    ("RUTA", r"\bruta\s+([a-z0-9\- ]+?)(?=\s+en\s+|\s+distrito|\s+distritos|\s+provincia|\s+region|$)"),
    ("CIRCUITO", r"\bcircuito\s+(?:turistico\s+)?([a-z0-9\- ]+?)(?=\s+en\s+|\s+distrito|\s+distritos|\s+provincia|\s+region|$)")
]


PALABRAS_CORTE = [
    "servicio",
    "servicios",
    "turistico",
    "turisticos",
    "publicos",
    "centro",
    "poblado",
    "distrito",
    "provincia",
    "departamento",
    "region"
]


def limpiar_recurso(nombre):
    nombre = normalizar(nombre)

    tokens = nombre.split()
    limpio = []

    for token in tokens:
        if token in PALABRAS_CORTE:
            break

        limpio.append(token)

    nombre = " ".join(limpio).strip()

    nombre = re.sub(
        r"^(de|del|la|el|los|las)\s+",
        "",
        nombre
    )

    return nombre.strip(" -")


def extraer_recursos(texto):
    resultados = []

    for tipo, patron in PATRONES:
        encontrados = re.findall(
            patron,
            texto
        )

        for nombre in encontrados:
            nombre = limpiar_recurso(nombre)

            if len(nombre) >= 3:
                resultados.append(
                    f"{tipo}: {nombre}"
                )

    return sorted(set(resultados))


# ============================================================
# ÁMBITO REFINADO
# ============================================================

def detectar_ambito(texto):

    if contiene_alguno(
        texto,
        ["montana", "cordillera", "nevado", "glaciar"]
    ):
        return "ANDINO / MONTAÑA"

    if contiene_alguno(
        texto,
        ["bosque", "selva", "amazonia", "biodiversidad"]
    ):
        return "AMAZÓNICO / BOSQUE"

    if contiene_alguno(
        texto,
        MARINO_COSTERO
    ):
        return "MARINO / COSTERO"

    if contiene_alguno(
        texto,
        ["laguna", "lago"]
    ):
        return "LACUSTRE"

    if contiene_alguno(
        texto,
        ["rio", "catarata", "cascada", "quebrada"]
    ):
        return "FLUVIAL"

    if contiene(
        texto,
        "canon"
    ):
        return "CAÑÓN / AVENTURA"

    if contiene_alguno(
        texto,
        ["parque nacional", "reserva nacional", "area natural", "santuario"]
    ):
        return "ÁREA NATURAL"

    if contiene_alguno(
        texto,
        ["camino inca", "qhapac nan", "qhapaq nan"]
    ):
        return "RUTA PATRIMONIAL / TREKKING"

    if contiene_alguno(
        texto,
        ["valle", "paisaje"]
    ):
        return "VALLE / PAISAJE"

    return "OTRO / NO DETERMINADO"


# ============================================================
# VOCACIÓN TERRITORIAL NATURALEZA / AVENTURA
# ============================================================

def vocacion_territorial(texto):

    puntaje = 0
    razones = []

    if contiene_alguno(texto, NATURALEZA_ALTA):
        puntaje += 3
        razones.append("RECURSO_NATURAL")

    if contiene_alguno(
        texto,
        ["camino inca", "qhapac nan", "qhapaq nan"]
    ):
        puntaje += 3
        razones.append("RUTA_PATRIMONIAL")

    if contiene_alguno(
        texto,
        ["sendero", "ruta", "circuito", "camino"]
    ):
        puntaje += 2
        razones.append("RUTA_CIRCUITO")

    if contiene_alguno(texto, MARINO_COSTERO):
        puntaje += 2
        razones.append("MARINO_COSTERO")

    if contiene_alguno(texto, PAISAJE):
        puntaje += 1
        razones.append("PAISAJE")

    if contiene_alguno(texto, TURISMO):
        puntaje += 1
        razones.append("EVIDENCIA_TURISTICA")

    if contiene_alguno(texto, INFRAESTRUCTURA):
        puntaje += 1
        razones.append("INFRAESTRUCTURA_HABILITANTE")

    if puntaje >= 6:
        nivel = "ALTA"
    elif puntaje >= 4:
        nivel = "MEDIA"
    elif puntaje >= 2:
        nivel = "BAJA"
    else:
        nivel = "NO DETERMINADA"

    return nivel, razones, puntaje


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():

    print("=" * 100)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("11B - REFINAMIENTO TERRITORIAL")
    print("=" * 100)

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Base_Destinos"
    )

    print(
        f"\nRegistros cargados: {len(df):,}"
    )

    df["Texto_11B"] = (
        df["Proyecto"]
        .fillna("")
        .astype(str)
        .apply(normalizar)
    )

    # --------------------------------------------------------
    # RECURSOS REFINADOS
    # --------------------------------------------------------

    df["Recursos_Refinados"] = (
        df["Texto_11B"]
        .apply(extraer_recursos)
    )

    # --------------------------------------------------------
    # ÁMBITO REFINADO
    # --------------------------------------------------------

    df["Ambito_Turistico_11B"] = (
        df["Texto_11B"]
        .apply(detectar_ambito)
    )

    # --------------------------------------------------------
    # VOCACIÓN
    # --------------------------------------------------------

    resultados = (
        df["Texto_11B"]
        .apply(vocacion_territorial)
    )

    df["Vocacion_Territorial_NA"] = (
        resultados
        .apply(lambda x: x[0])
    )

    df["Razones_Vocacion"] = (
        resultados
        .apply(
            lambda x:
            ", ".join(x[1])
        )
    )

    df["Puntaje_Vocacion"] = (
        resultados
        .apply(lambda x: x[2])
    )

    # Convertir recursos a texto
    df["Recursos_Refinados"] = (
        df["Recursos_Refinados"]
        .apply(
            lambda x:
            " | ".join(x)
        )
    )

    # ========================================================
    # RESUMEN VOCACIÓN
    # ========================================================

    resumen_vocacion = (
        df.groupby(
            "Vocacion_Territorial_NA",
            as_index=False
        )
        .agg(
            Registros=("ID_Radar", "count"),
            PIM=("PIM", "sum"),
            Devengado=("Devengado", "sum")
        )
    )

    pim_total = df["PIM"].sum()

    resumen_vocacion["Peso_PIM_Radar"] = (
        resumen_vocacion["PIM"]
        / pim_total
        * 100
    )

    resumen_vocacion["Avance_Porcentaje"] = (
        resumen_vocacion["Devengado"]
        / resumen_vocacion["PIM"]
        * 100
    ).fillna(0)

    # ========================================================
    # RESUMEN ÁMBITOS
    # ========================================================

    resumen_ambito = (
        df.groupby(
            "Ambito_Turistico_11B",
            as_index=False
        )
        .agg(
            Registros=("ID_Radar", "count"),
            PIM=("PIM", "sum"),
            Devengado=("Devengado", "sum")
        )
    )

    resumen_ambito["Peso_PIM_Radar"] = (
        resumen_ambito["PIM"]
        / pim_total
        * 100
    )

    resumen_ambito["Avance_Porcentaje"] = (
        resumen_ambito["Devengado"]
        / resumen_ambito["PIM"]
        * 100
    ).fillna(0)

    resumen_ambito = resumen_ambito.sort_values(
        "PIM",
        ascending=False
    )

    # ========================================================
    # CASOS DE ALTA VOCACIÓN
    # ========================================================

    alta = df[
        df["Vocacion_Territorial_NA"]
        == "ALTA"
    ].copy()

    alta = alta[
        [
            "Departamento",
            "Codigo_Proyecto",
            "Proyecto",
            "Recursos_Refinados",
            "Ambito_Turistico_11B",
            "Vocacion_Territorial_NA",
            "Puntaje_Vocacion",
            "Razones_Vocacion",
            "Nivel_Evidencia_Aventura",
            "PIM",
            "Devengado"
        ]
    ]

    alta = alta.sort_values(
        "PIM",
        ascending=False
    )

    # ========================================================
    # MOSTRAR RESULTADOS
    # ========================================================

    print("\n" + "=" * 100)
    print("VOCACIÓN TERRITORIAL NATURALEZA / AVENTURA")
    print("=" * 100)

    print(
        resumen_vocacion.to_string(
            index=False,
            formatters={
                "PIM":
                    lambda x: f"{x:,.0f}",
                "Devengado":
                    lambda x: f"{x:,.0f}",
                "Peso_PIM_Radar":
                    lambda x: f"{x:.1f}%",
                "Avance_Porcentaje":
                    lambda x: f"{x:.1f}%"
            }
        )
    )

    print("\n" + "=" * 100)
    print("ÁMBITOS TERRITORIALES REFINADOS")
    print("=" * 100)

    print(
        resumen_ambito.to_string(
            index=False,
            formatters={
                "PIM":
                    lambda x: f"{x:,.0f}",
                "Devengado":
                    lambda x: f"{x:,.0f}",
                "Peso_PIM_Radar":
                    lambda x: f"{x:.1f}%",
                "Avance_Porcentaje":
                    lambda x: f"{x:.1f}%"
            }
        )
    )

    print("\n" + "=" * 100)
    print("TOP 20 PROYECTOS DE ALTA VOCACIÓN")
    print("=" * 100)

    print(
        alta.head(20).to_string(
            index=False,
            formatters={
                "PIM":
                    lambda x: f"{x:,.0f}",
                "Devengado":
                    lambda x: f"{x:,.0f}"
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
        f"REGISTROS RADAR : {len(df):,}"
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
        f"ALTA VOCACIÓN   : {len(alta):,}"
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
            sheet_name="Base_Refinada_11B",
            index=False
        )

        resumen_vocacion.to_excel(
            writer,
            sheet_name="Vocacion_Territorial",
            index=False
        )

        resumen_ambito.to_excel(
            writer,
            sheet_name="Ambitos_Refinados",
            index=False
        )

        alta.to_excel(
            writer,
            sheet_name="Alta_Vocacion",
            index=False
        )

    print("\nARCHIVO GENERADO:")
    print(SALIDA)

    print(
        "\n✓ REFINAMIENTO 11B COMPLETADO"
    )

    print("FIN")


if __name__ == "__main__":
    main()