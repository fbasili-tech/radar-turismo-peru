from pathlib import Path
import pandas as pd
import re
import unicodedata

# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 3: CLASIFICACIÓN AUTOMÁTICA DE PROYECTOS
# ============================================================

ARCHIVO_ENTRADA = Path("outputs/radar_turismo_proyectos_peru_2026.xlsx")
ARCHIVO_SALIDA = Path("outputs/radar_turismo_clasificado_peru_2026.xlsx")


# ------------------------------------------------------------
# 1. NORMALIZACIÓN DE TEXTO
# ------------------------------------------------------------

def normalizar_texto(texto):
    """
    Convierte el texto a minúsculas, elimina tildes
    y caracteres especiales para facilitar búsquedas.
    """
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


# ------------------------------------------------------------
# 2. DICCIONARIOS DEL RADAR
# ------------------------------------------------------------

PALABRAS_NATURALEZA = [
    "naturaleza",
    "natural",
    "paisaje",
    "paisajistico",
    "bosque",
    "selva",
    "amazonia",
    "amazonico",
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
    "mar",
    "isla",
    "reserva",
    "parque nacional",
    "area natural",
    "area protegida",
    "anp",
    "biodiversidad",
    "fauna",
    "flora",
    "avistamiento",
    "observacion de aves",
    "birdwatching",
    "ecoturismo"
]

PALABRAS_AVENTURA = [
    "aventura",
    "trekking",
    "senderismo",
    "caminata",
    "ruta de caminata",
    "sendero",
    "montanismo",
    "andinismo",
    "escalada",
    "rapel",
    "rappel",
    "canotaje",
    "rafting",
    "kayak",
    "kayaking",
    "canoa",
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
    "via ferrata",
    "barranquismo",
    "canyoning",
    "sandboard"
]

PALABRAS_CULTURA = [
    "arqueologico",
    "arqueologica",
    "patrimonio",
    "cultural",
    "museo",
    "iglesia",
    "templo",
    "centro historico",
    "sitio historico",
    "camino inca",
    "qhapac nan",
    "comunidad nativa",
    "comunidad campesina",
    "artesania"
]

PALABRAS_INFRAESTRUCTURA = [
    "mirador",
    "sendero",
    "malecon",
    "embarcadero",
    "muelle",
    "centro de interpretacion",
    "centro de visitantes",
    "servicios turisticos",
    "infraestructura turistica",
    "senalizacion",
    "señalizacion",
    "parador",
    "refugio",
    "campamento",
    "boleteria",
    "estacionamiento",
    "servicios higienicos",
    "acondicionamiento turistico"
]

PALABRAS_ACCESIBILIDAD = [
    "acceso",
    "accesibilidad",
    "carretera",
    "camino",
    "trocha",
    "via",
    "puente",
    "pista",
    "transporte",
    "teleferico"
]

PALABRAS_TURISMO = [
    "turismo",
    "turistico",
    "turistica",
    "turistas",
    "visitante",
    "visitantes",
    "destino turistico",
    "recurso turistico",
    "atractivo turistico",
    "servicio turistico"
]


# ------------------------------------------------------------
# 3. FUNCIONES DE CLASIFICACIÓN
# ------------------------------------------------------------

def contiene(texto, palabras):
    return any(palabra in texto for palabra in palabras)


def encontrar_coincidencias(texto, palabras):
    encontrados = []

    for palabra in palabras:
        if palabra in texto:
            encontrados.append(palabra)

    return ", ".join(sorted(set(encontrados)))


def clasificar_tipo(texto):

    naturaleza = contiene(texto, PALABRAS_NATURALEZA)
    aventura = contiene(texto, PALABRAS_AVENTURA)
    cultura = contiene(texto, PALABRAS_CULTURA)
    infraestructura = contiene(texto, PALABRAS_INFRAESTRUCTURA)
    accesibilidad = contiene(texto, PALABRAS_ACCESIBILIDAD)
    turismo = contiene(texto, PALABRAS_TURISMO)

    if naturaleza and aventura:
        return "Naturaleza y Aventura"

    if aventura:
        return "Aventura"

    if naturaleza:
        return "Naturaleza"

    if cultura:
        return "Cultural"

    if infraestructura and turismo:
        return "Infraestructura Turística"

    if accesibilidad and turismo:
        return "Accesibilidad Turística"

    if turismo:
        return "Turismo General"

    return "Otros"


def calcular_prioridad(texto):

    puntaje = 0

    if contiene(texto, PALABRAS_TURISMO):
        puntaje += 2

    if contiene(texto, PALABRAS_NATURALEZA):
        puntaje += 3

    if contiene(texto, PALABRAS_AVENTURA):
        puntaje += 4

    if contiene(texto, PALABRAS_INFRAESTRUCTURA):
        puntaje += 2

    if contiene(texto, PALABRAS_ACCESIBILIDAD):
        puntaje += 1

    if contiene(texto, PALABRAS_CULTURA):
        puntaje += 1

    if puntaje >= 7:
        return "MUY ALTA"

    if puntaje >= 5:
        return "ALTA"

    if puntaje >= 3:
        return "MEDIA"

    if puntaje >= 1:
        return "BAJA"

    return "NO CLASIFICADO"


# ------------------------------------------------------------
# 4. BUSCAR AUTOMÁTICAMENTE LA COLUMNA DEL PROYECTO
# ------------------------------------------------------------

def detectar_columna_nombre(df):

    candidatos = [
        "Proyecto",
        "Nombre_Proyecto",
        "Nombre Proyecto",
        "Proyecto_Nombre",
        "Descripcion",
        "Descripción",
        "Nombre",
        "Producto_Proyecto"
    ]

    for columna in candidatos:
        if columna in df.columns:
            return columna

    # búsqueda flexible
    for columna in df.columns:

        col = normalizar_texto(columna)

        if "proyecto" in col and (
            "nombre" in col
            or "descripcion" in col
            or col == "proyecto"
        ):
            return columna

    raise ValueError(
        "No se encontró automáticamente la columna con el nombre del proyecto."
    )


# ------------------------------------------------------------
# 5. PROCESO PRINCIPAL
# ------------------------------------------------------------

def main():

    print("=" * 80)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("CLASIFICANDO BASE NACIONAL")
    print("=" * 80)

    if not ARCHIVO_ENTRADA.exists():

        print("\nERROR:")
        print(f"No se encontró el archivo:\n{ARCHIVO_ENTRADA}")
        return

    # Leer Excel
    df = pd.read_excel(ARCHIVO_ENTRADA)

    print(f"\nRegistros cargados: {len(df):,}")
    print(f"Columnas disponibles: {len(df.columns)}")

    columna_proyecto = detectar_columna_nombre(df)

    print(f"\nColumna utilizada para clasificación:")
    print(columna_proyecto)

    # Crear texto normalizado
    df["_texto_radar"] = (
        df[columna_proyecto]
        .fillna("")
        .astype(str)
        .apply(normalizar_texto)
    )

    # --------------------------------------------------------
    # VARIABLES DEL RADAR
    # --------------------------------------------------------

    df["Naturaleza"] = df["_texto_radar"].apply(
        lambda x: "SI" if contiene(x, PALABRAS_NATURALEZA) else "NO"
    )

    df["Aventura"] = df["_texto_radar"].apply(
        lambda x: "SI" if contiene(x, PALABRAS_AVENTURA) else "NO"
    )

    df["Cultural"] = df["_texto_radar"].apply(
        lambda x: "SI" if contiene(x, PALABRAS_CULTURA) else "NO"
    )

    df["Infraestructura_Turistica"] = df["_texto_radar"].apply(
        lambda x: "SI" if contiene(x, PALABRAS_INFRAESTRUCTURA) else "NO"
    )

    df["Accesibilidad"] = df["_texto_radar"].apply(
        lambda x: "SI" if contiene(x, PALABRAS_ACCESIBILIDAD) else "NO"
    )

    df["Tipo_Turismo"] = df["_texto_radar"].apply(
        clasificar_tipo
    )

    df["Prioridad_Radar"] = df["_texto_radar"].apply(
        calcular_prioridad
    )

    df["Palabras_Clave_Naturaleza"] = df["_texto_radar"].apply(
        lambda x: encontrar_coincidencias(
            x,
            PALABRAS_NATURALEZA
        )
    )

    df["Palabras_Clave_Aventura"] = df["_texto_radar"].apply(
        lambda x: encontrar_coincidencias(
            x,
            PALABRAS_AVENTURA
        )
    )

    # --------------------------------------------------------
    # IDENTIFICACIÓN ESPECIAL DEL RADAR
    # --------------------------------------------------------

    df["Radar_Naturaleza_Aventura"] = (
        (df["Naturaleza"] == "SI")
        | (df["Aventura"] == "SI")
    ).map({
        True: "SI",
        False: "NO"
    })

    # Quitar columna auxiliar
    df.drop(columns=["_texto_radar"], inplace=True)

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("RESULTADOS DE CLASIFICACIÓN")
    print("=" * 80)

    print("\nTIPO DE TURISMO:")
    print(
        df["Tipo_Turismo"]
        .value_counts()
        .to_string()
    )

    print("\nPRIORIDAD RADAR:")
    print(
        df["Prioridad_Radar"]
        .value_counts()
        .to_string()
    )

    total_na = (
        df["Radar_Naturaleza_Aventura"] == "SI"
    ).sum()

    print("\nPROYECTOS VINCULADOS A NATURALEZA / AVENTURA:")
    print(f"{total_na:,} de {len(df):,}")

    porcentaje = (
        total_na / len(df) * 100
        if len(df) > 0
        else 0
    )

    print(f"{porcentaje:.1f}% de la base nacional")

    # --------------------------------------------------------
    # GUARDAR EXCEL
    # --------------------------------------------------------

    ARCHIVO_SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with pd.ExcelWriter(
        ARCHIVO_SALIDA,
        engine="openpyxl"
    ) as writer:

        # Base completa
        df.to_excel(
            writer,
            sheet_name="Base_Clasificada",
            index=False
        )

        # Solo naturaleza / aventura
        df_na = df[
            df["Radar_Naturaleza_Aventura"] == "SI"
        ]

        df_na.to_excel(
            writer,
            sheet_name="Naturaleza_Aventura",
            index=False
        )

        # Resumen tipo turismo
        resumen_tipo = (
            df["Tipo_Turismo"]
            .value_counts()
            .reset_index()
        )

        resumen_tipo.columns = [
            "Tipo_Turismo",
            "Proyectos"
        ]

        resumen_tipo.to_excel(
            writer,
            sheet_name="Resumen_Tipo",
            index=False
        )

        # Resumen prioridad
        resumen_prioridad = (
            df["Prioridad_Radar"]
            .value_counts()
            .reset_index()
        )

        resumen_prioridad.columns = [
            "Prioridad_Radar",
            "Proyectos"
        ]

        resumen_prioridad.to_excel(
            writer,
            sheet_name="Resumen_Prioridad",
            index=False
        )

    print("\n" + "=" * 80)
    print("ARCHIVO GENERADO")
    print("=" * 80)

    print(ARCHIVO_SALIDA)

    print("\n✓ CLASIFICACIÓN DEL RADAR COMPLETADA")
    print("\nFIN")


if __name__ == "__main__":
    main()