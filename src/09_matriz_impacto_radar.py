from pathlib import Path
import pandas as pd
import unicodedata
import re

# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 09: MATRIZ DE IMPACTO MULTIDIMENSIONAL
# ============================================================

ENTRADA = Path(
    "outputs/radar_turismo_tipologia_inversion_2026.xlsx"
)

SALIDA = Path(
    "outputs/radar_turismo_matriz_impacto_2026.xlsx"
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

    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


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
# 1. ECOSISTEMAS / ENTORNOS
# ============================================================

ECOSISTEMAS = {

    "MONTANA": [
        "montana",
        "montanas",
        "cordillera",
        "nevado",
        "nevados",
        "glaciar",
        "glaciares",
        "alta montana"
    ],

    "LACUSTRE": [
        "lago",
        "lagos",
        "laguna",
        "lagunas"
    ],

    "FLUVIAL": [
        "rio",
        "rios",
        "catarata",
        "cataratas",
        "cascada",
        "cascadas",
        "quebrada"
    ],

    "MARINO_COSTERO": [
        "mar",
        "marino",
        "marina",
        "playa",
        "playas",
        "isla",
        "islas",
        "bahia",
        "litoral",
        "costa"
    ],

    "BOSQUE_SELVA": [
        "bosque",
        "bosques",
        "selva",
        "amazonia",
        "amazonico",
        "biodiversidad",
        "flora",
        "fauna"
    ],

    "AREAS_NATURALES": [
        "parque nacional",
        "reserva nacional",
        "reserva natural",
        "santuario nacional",
        "area natural",
        "area protegida"
    ],

    "VALLE_PAISAJE": [
        "valle",
        "paisaje",
        "paisajistico"
    ]
}


# ============================================================
# 2. ACTIVIDADES / PRODUCTOS
# ============================================================

PRODUCTOS = {

    "TREKKING_SENDERISMO": [
        "trekking",
        "senderismo",
        "caminata",
        "sendero",
        "senderos"
    ],

    "MONTANISMO": [
        "montanismo",
        "andinismo",
        "escalada"
    ],

    "AVENTURA_ACUATICA": [
        "rafting",
        "canotaje",
        "kayak",
        "buceo",
        "snorkel",
        "surf"
    ],

    "CICLISMO": [
        "ciclismo",
        "bicicleta",
        "mountain bike"
    ],

    "AVENTURA_AEREA": [
        "parapente",
        "tirolesa",
        "zipline"
    ],

    "OBSERVACION_NATURALEZA": [
        "observacion",
        "avistamiento",
        "flora",
        "fauna",
        "aves",
        "birdwatching"
    ],

    "RUTAS_CIRCUITOS": [
        "ruta",
        "rutas",
        "circuito",
        "circuitos"
    ],

    "CAMPAMENTO": [
        "campamento",
        "camping"
    ]
}


# ============================================================
# 3. TIPOS DE INTERVENCIÓN PÚBLICA
# ============================================================

INTERVENCIONES = {

    "SENDEROS_RUTAS": [
        "sendero",
        "senderos",
        "ruta",
        "rutas",
        "camino",
        "caminos",
        "circuito",
        "circuitos"
    ],

    "MIRADORES": [
        "mirador",
        "miradores"
    ],

    "EMBARCADEROS_MUELLES": [
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

    "INFRAESTRUCTURA_SERVICIOS": [
        "infraestructura turistica",
        "acondicionamiento turistico",
        "servicio turistico",
        "servicios turisticos",
        "instalacion turistica",
        "instalaciones turisticas",
        "servicios higienicos",
        "estacionamiento",
        "senalizacion"
    ],

    "RECREACION_ESPACIO_PUBLICO": [
        "recreacion",
        "recreativo",
        "recreativa",
        "espacio publico",
        "espacios publicos"
    ],

    "EQUIPAMIENTO": [
        "equipamiento",
        "equipo",
        "mobiliario"
    ]
}


# ============================================================
# FUNCIONES DE DETECCIÓN
# ============================================================

def detectar_dimensiones(texto, diccionario):

    encontrados = []

    for categoria, palabras in diccionario.items():

        if contiene_alguno(
            texto,
            palabras
        ):
            encontrados.append(
                categoria
            )

    return encontrados


def unir(lista):

    if not lista:
        return ""

    return ", ".join(lista)


# ============================================================
# NIVEL DE RELACIÓN CON NATURALEZA / AVENTURA
# ============================================================

def nivel_impacto(row):

    vinculo = row["Vinculacion_Radar_V2"]

    ecosistemas = row["Ecosistemas"]
    productos = row["Productos_NA"]

    if vinculo == "DIRECTA" and productos:
        return "NUCLEO NATURALEZA/AVENTURA"

    if vinculo == "DIRECTA" and ecosistemas:
        return "NUCLEO NATURALEZA/AVENTURA"

    if vinculo == "COMPLEMENTARIA":
        return "SOPORTE AL DESTINO"

    return "OTRO"


# ============================================================
# PROCESO
# ============================================================

def main():

    print("=" * 95)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("MATRIZ DE IMPACTO MULTIDIMENSIONAL")
    print("=" * 95)

    # --------------------------------------------------------
    # CARGAR BASE DEL 08
    # --------------------------------------------------------

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Base_Tipologias"
    )

    print(
        f"\nRegistros núcleo Radar cargados: {len(df):,}"
    )

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    df["Texto_Impacto"] = (
        df["Proyecto"]
        .fillna("")
        .astype(str)
        .apply(normalizar)
    )

    # --------------------------------------------------------
    # DETECCIÓN MULTIDIMENSIONAL
    # --------------------------------------------------------

    df["Ecosistemas"] = (
        df["Texto_Impacto"]
        .apply(
            lambda x:
            detectar_dimensiones(
                x,
                ECOSISTEMAS
            )
        )
    )

    df["Productos_NA"] = (
        df["Texto_Impacto"]
        .apply(
            lambda x:
            detectar_dimensiones(
                x,
                PRODUCTOS
            )
        )
    )

    df["Intervenciones"] = (
        df["Texto_Impacto"]
        .apply(
            lambda x:
            detectar_dimensiones(
                x,
                INTERVENCIONES
            )
        )
    )

    # Mantener listas temporalmente para clasificación
    df["Nivel_Impacto"] = (
        df.apply(
            nivel_impacto,
            axis=1
        )
    )

    # --------------------------------------------------------
    # VARIABLES BINARIAS
    # --------------------------------------------------------

    for categoria in ECOSISTEMAS.keys():

        df[
            f"ECO_{categoria}"
        ] = df["Ecosistemas"].apply(
            lambda x:
            1 if categoria in x else 0
        )

    for categoria in PRODUCTOS.keys():

        df[
            f"PROD_{categoria}"
        ] = df["Productos_NA"].apply(
            lambda x:
            1 if categoria in x else 0
        )

    for categoria in INTERVENCIONES.keys():

        df[
            f"INT_{categoria}"
        ] = df["Intervenciones"].apply(
            lambda x:
            1 if categoria in x else 0
        )

    # --------------------------------------------------------
    # CONVERTIR LISTAS A TEXTO
    # --------------------------------------------------------

    df["Ecosistemas"] = (
        df["Ecosistemas"]
        .apply(unir)
    )

    df["Productos_NA"] = (
        df["Productos_NA"]
        .apply(unir)
    )

    df["Intervenciones"] = (
        df["Intervenciones"]
        .apply(unir)
    )

    # --------------------------------------------------------
    # AVANCE
    # --------------------------------------------------------

    df["Avance_Radar"] = (
        df["Devengado"]
        / df["PIM"]
        * 100
    ).fillna(0)

    # ========================================================
    # RESUMEN POR NIVEL DE IMPACTO
    # ========================================================

    impacto = (
        df.groupby(
            "Nivel_Impacto",
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

    pim_radar = df["PIM"].sum()

    impacto["Peso_PIM_Radar"] = (
        impacto["PIM"]
        / pim_radar
        * 100
    )

    impacto["Avance_Porcentaje"] = (
        impacto["Devengado"]
        / impacto["PIM"]
        * 100
    ).fillna(0)

    # ========================================================
    # RESUMEN POR ECOSISTEMA
    # ========================================================

    filas_eco = []

    for categoria in ECOSISTEMAS.keys():

        mascara = (
            df[f"ECO_{categoria}"] == 1
        )

        sub = df[mascara]

        filas_eco.append(
            {
                "Ecosistema": categoria,
                "Registros": len(sub),
                "PIM": sub["PIM"].sum(),
                "Devengado": sub["Devengado"].sum()
            }
        )

    resumen_ecosistemas = pd.DataFrame(
        filas_eco
    )

    resumen_ecosistemas[
        "Peso_PIM_Radar"
    ] = (
        resumen_ecosistemas["PIM"]
        / pim_radar
        * 100
    )

    resumen_ecosistemas[
        "Avance_Porcentaje"
    ] = (
        resumen_ecosistemas["Devengado"]
        / resumen_ecosistemas["PIM"]
        * 100
    ).fillna(0)

    resumen_ecosistemas = (
        resumen_ecosistemas
        .sort_values(
            "PIM",
            ascending=False
        )
    )

    # ========================================================
    # RESUMEN PRODUCTOS
    # ========================================================

    filas_prod = []

    for categoria in PRODUCTOS.keys():

        mascara = (
            df[f"PROD_{categoria}"] == 1
        )

        sub = df[mascara]

        filas_prod.append(
            {
                "Producto": categoria,
                "Registros": len(sub),
                "PIM": sub["PIM"].sum(),
                "Devengado": sub["Devengado"].sum()
            }
        )

    resumen_productos = pd.DataFrame(
        filas_prod
    )

    resumen_productos[
        "Peso_PIM_Radar"
    ] = (
        resumen_productos["PIM"]
        / pim_radar
        * 100
    )

    resumen_productos[
        "Avance_Porcentaje"
    ] = (
        resumen_productos["Devengado"]
        / resumen_productos["PIM"]
        * 100
    ).fillna(0)

    resumen_productos = (
        resumen_productos
        .sort_values(
            "PIM",
            ascending=False
        )
    )

    # ========================================================
    # RESUMEN INTERVENCIONES
    # ========================================================

    filas_int = []

    for categoria in INTERVENCIONES.keys():

        mascara = (
            df[f"INT_{categoria}"] == 1
        )

        sub = df[mascara]

        filas_int.append(
            {
                "Intervencion": categoria,
                "Registros": len(sub),
                "PIM": sub["PIM"].sum(),
                "Devengado": sub["Devengado"].sum()
            }
        )

    resumen_intervenciones = pd.DataFrame(
        filas_int
    )

    resumen_intervenciones[
        "Peso_PIM_Radar"
    ] = (
        resumen_intervenciones["PIM"]
        / pim_radar
        * 100
    )

    resumen_intervenciones[
        "Avance_Porcentaje"
    ] = (
        resumen_intervenciones["Devengado"]
        / resumen_intervenciones["PIM"]
        * 100
    ).fillna(0)

    resumen_intervenciones = (
        resumen_intervenciones
        .sort_values(
            "PIM",
            ascending=False
        )
    )

    # ========================================================
    # MATRIZ TERRITORIAL
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
            )
        )
    )

    territorial["Avance_Radar"] = (
        territorial["Devengado_Radar"]
        / territorial["PIM_Radar"]
        * 100
    ).fillna(0)

    territorial = territorial.sort_values(
        "PIM_Radar",
        ascending=False
    )

    # ========================================================
    # RESULTADOS
    # ========================================================

    print("\n" + "=" * 95)
    print("NIVEL DE IMPACTO")
    print("=" * 95)

    print(
        impacto.to_string(
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

    print("\n" + "=" * 95)
    print("ECOSISTEMAS / ENTORNOS")
    print("=" * 95)

    print(
        resumen_ecosistemas.to_string(
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

    print("\n" + "=" * 95)
    print("PRODUCTOS / ACTIVIDADES")
    print("=" * 95)

    print(
        resumen_productos.to_string(
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

    print("\n" + "=" * 95)
    print("TIPOS DE INTERVENCIÓN")
    print("=" * 95)

    print(
        resumen_intervenciones.to_string(
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

    # ========================================================
    # CONTROL
    # ========================================================

    print("\n" + "=" * 95)
    print("CONTROL")
    print("=" * 95)

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

    # ========================================================
    # EXPORTAR
    # ========================================================

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Matriz_Impacto",
            index=False
        )

        impacto.to_excel(
            writer,
            sheet_name="Nivel_Impacto",
            index=False
        )

        resumen_ecosistemas.to_excel(
            writer,
            sheet_name="Ecosistemas",
            index=False
        )

        resumen_productos.to_excel(
            writer,
            sheet_name="Productos",
            index=False
        )

        resumen_intervenciones.to_excel(
            writer,
            sheet_name="Intervenciones",
            index=False
        )

        territorial.to_excel(
            writer,
            sheet_name="Territorial",
            index=False
        )

    print("\nARCHIVO GENERADO:")
    print(SALIDA)

    print(
        "\n✓ MATRIZ DE IMPACTO COMPLETADA"
    )

    print("FIN")


if __name__ == "__main__":
    main()