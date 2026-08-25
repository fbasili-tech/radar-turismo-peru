from pathlib import Path
import re
import unicodedata
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# FASE 2
# ETAPA 19: HOSPEDAJE, PERMANENCIA Y OCUPABILIDAD
# VERSIÓN DEFINITIVA
# ============================================================

URL_DATASET = (
    "https://www.datosabiertos.gob.pe/dataset/"
    "indicadores-de-ocupabilidad-ministerio-de-comercio-"
    "exterior-y-turismo-mincetur"
)

CARPETA_RAW = Path("data/fase2_raw")
CARPETA_OUTPUTS = Path("outputs")

CARPETA_RAW.mkdir(parents=True, exist_ok=True)
CARPETA_OUTPUTS.mkdir(parents=True, exist_ok=True)

CSV_LOCAL = Path(
    "data/mincetur_indicadores_ocupabilidad.csv"
)

CSV_DESCARGADO = Path(
    "data/fase2_raw/mincetur_indicadores_ocupabilidad.csv"
)

SALIDA = Path(
    "outputs/radar_fase2_hospedaje_permanencia_2026.xlsx"
)


# ============================================================
# CATÁLOGO TERRITORIAL
# ============================================================

DEPARTAMENTOS_PERU = [
    "AMAZONAS",
    "ANCASH",
    "APURIMAC",
    "AREQUIPA",
    "AYACUCHO",
    "CAJAMARCA",
    "CUSCO",
    "HUANCAVELICA",
    "HUANUCO",
    "ICA",
    "JUNIN",
    "LA LIBERTAD",
    "LAMBAYEQUE",
    "LIMA",
    "LORETO",
    "MADRE DE DIOS",
    "MOQUEGUA",
    "PASCO",
    "PIURA",
    "PROVINCIA CONSTITUCIONAL DEL CALLAO",
    "PUNO",
    "SAN MARTIN",
    "TACNA",
    "TUMBES",
    "UCAYALI"
]


# ============================================================
# NORMALIZACIÓN
# ============================================================

def normalizar_texto(valor):

    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    texto = texto.upper()

    texto = re.sub(
        r"[^A-Z0-9 ]",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def homologar_departamento(valor):

    valor = normalizar_texto(valor)

    equivalencias = {
        "CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO",

        "PROVINCIA CONSTITUCIONAL CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO",

        "PROVINCIA CONSTITUCIONAL DEL CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO"
    }

    return equivalencias.get(
        valor,
        valor
    )


# ============================================================
# WEB
# ============================================================

def crear_sesion():

    sesion = requests.Session()

    sesion.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/151 Safari/537.36"
            ),
            "Accept-Language":
                "es-PE,es;q=0.9,en;q=0.8"
        }
    )

    return sesion


def descubrir_csv():

    print(
        "\nBuscando recursos oficiales "
        "de ocupabilidad..."
    )

    sesion = crear_sesion()

    try:

        respuesta = sesion.get(
            URL_DATASET,
            timeout=40
        )

        print(
            f"Respuesta catálogo: "
            f"{respuesta.status_code}"
        )

        if respuesta.status_code != 200:
            return None

        soup = BeautifulSoup(
            respuesta.text,
            "html.parser"
        )

        candidatos = []

        for enlace in soup.find_all(
            "a",
            href=True
        ):

            href = enlace.get(
                "href",
                ""
            )

            texto = enlace.get_text(
                " ",
                strip=True
            )

            combinado = (
                texto
                + " "
                + href
            ).lower()

            if (
                "2025" in combinado
                and (
                    ".csv" in combinado
                    or "/resource/" in href
                )
            ):

                candidatos.append(
                    (
                        texto,
                        urljoin(
                            URL_DATASET,
                            href
                        )
                    )
                )

        print(
            f"Recursos 2025 candidatos: "
            f"{len(candidatos)}"
        )

        for texto, url in candidatos:

            try:

                r = sesion.get(
                    url,
                    timeout=30
                )

                if r.status_code != 200:
                    continue

                soup_r = BeautifulSoup(
                    r.text,
                    "html.parser"
                )

                for enlace in soup_r.find_all(
                    "a",
                    href=True
                ):

                    href = enlace[
                        "href"
                    ]

                    contenido = (
                        enlace.get_text(
                            " ",
                            strip=True
                        )
                        + " "
                        + href
                    ).lower()

                    if ".csv" in contenido:

                        return (
                            urljoin(
                                url,
                                href
                            ),
                            texto
                        )

            except Exception:
                continue

        for texto, url in candidatos:

            if ".csv" in url.lower():

                return (
                    url,
                    texto
                )

        return None

    except Exception as error:

        print(
            f"Error consultando catálogo: "
            f"{error}"
        )

        return None


def descargar_csv(
    url,
    destino
):

    sesion = crear_sesion()

    print(
        "\nDescargando recurso..."
    )

    try:

        respuesta = sesion.get(
            url,
            timeout=90
        )

        print(
            f"Respuesta recurso: "
            f"{respuesta.status_code}"
        )

        if respuesta.status_code != 200:
            return False

        contenido = respuesta.content

        inicio = contenido[
            :300
        ].lower()

        if (
            b"<html" in inicio
            or b"<!doctype" in inicio
        ):

            print(
                "El recurso recibido parece HTML."
            )

            return False

        destino.write_bytes(
            contenido
        )

        print(
            f"Archivo descargado: "
            f"{destino}"
        )

        print(
            f"Tamaño: "
            f"{destino.stat().st_size:,} bytes"
        )

        return True

    except Exception as error:

        print(
            f"Error de descarga: "
            f"{error}"
        )

        return False


def obtener_archivo():

    if CSV_LOCAL.exists():

        print(
            "\nUsando archivo local:"
        )

        print(
            CSV_LOCAL
        )

        return (
            CSV_LOCAL,
            "ARCHIVO LOCAL"
        )

    if CSV_DESCARGADO.exists():

        print(
            "\nUsando descarga previa:"
        )

        print(
            CSV_DESCARGADO
        )

        return (
            CSV_DESCARGADO,
            "DESCARGA PREVIA"
        )

    resultado = descubrir_csv()

    if resultado:

        url, descripcion = resultado

        if descargar_csv(
            url,
            CSV_DESCARGADO
        ):

            return (
                CSV_DESCARGADO,
                descripcion
            )

    return (
        None,
        None
    )


# ============================================================
# LECTURA FLEXIBLE
# ============================================================

def leer_csv_flexible(ruta):

    codificaciones = [
        "utf-8-sig",
        "utf-8",
        "latin1",
        "cp1252"
    ]

    separadores = [
        ",",
        ";",
        "\t",
        "|"
    ]

    mejor = None

    for encoding in codificaciones:

        for separador in separadores:

            try:

                df = pd.read_csv(
                    ruta,
                    encoding=encoding,
                    sep=separador,
                    low_memory=False
                )

                if (
                    mejor is None
                    or len(df.columns)
                    > len(mejor.columns)
                ):
                    mejor = df

                if len(df.columns) >= 10:

                    print(
                        "\nCSV leído correctamente"
                    )

                    print(
                        f"Encoding : {encoding}"
                    )

                    print(
                        f"Separador: "
                        f"{repr(separador)}"
                    )

                    return df

            except Exception:
                continue

    if mejor is not None:
        return mejor

    raise RuntimeError(
        "No fue posible leer el archivo CSV."
    )


# ============================================================
# UTILIDADES
# ============================================================

def convertir_numero(serie):

    texto = (
        serie
        .astype(str)
        .str.strip()
        .str.replace(
            ",",
            "",
            regex=False
        )
        .str.replace(
            "%",
            "",
            regex=False
        )
    )

    return pd.to_numeric(
        texto,
        errors="coerce"
    )


# ============================================================
# PREPARAR BASE
# ============================================================

def preparar_base(df):

    columnas_requeridas = [
        "ANIO",
        "MES",
        "ID_CLASE",
        "CLASE",
        "ID_CATEGORIA",
        "CATEGORIA",
        "DEPARTAMENTO",
        "NUMERO_ESTABLECIMIENTOS",
        "NUMERO_HABITACIONES",
        "NUMERO_PLAZAS_CAMA",
        "PORCENTAJE_TNOH",
        "PORCENTAJE_TNOC",
        "PROMEDIO_PERMANENCIA",
        "PROMEDIO_PERMANENCIA_NAC",
        "PROMEDIO_PERMANENCIA_EXT",
        "TOTAL_ARRIBOS",
        "TOTAL_ARRIBOS_NAC",
        "TOTAL_ARRIBOS_EXT",
        "TOTAL_PERNOCT",
        "TOTAL_PERNOCT_NAC",
        "TOTAL_PERNOCT_EXT",
        "TOTAL_EMPLEO"
    ]

    faltantes = [
        c
        for c in columnas_requeridas
        if c not in df.columns
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(
                faltantes
            )
        )

    base = df.copy()

    base[
        "Departamento_Radar"
    ] = (
        base[
            "DEPARTAMENTO"
        ]
        .apply(
            homologar_departamento
        )
    )

    # --------------------------------------------------------
    # FILTRO CONSOLIDADO OFICIAL
    # --------------------------------------------------------

    consolidado = base[
        (
            base[
                "ID_CLASE"
            ]
            .astype(str)
            .str.strip()
            .str.upper()
            == "TT"
        )
        &
        (
            base[
                "ID_CATEGORIA"
            ]
            .astype(str)
            .str.strip()
            .str.upper()
            == "TT"
        )
    ].copy()

    print(
        "\n" + "=" * 100
    )

    print(
        "CONTROL DE CONSOLIDACIÓN"
    )

    print(
        "=" * 100
    )

    print(
        f"Registros originales     : "
        f"{len(base):,}"
    )

    print(
        f"Registros consolidados   : "
        f"{len(consolidado):,}"
    )

    print(
        "Filtro aplicado          : "
        "ID_CLASE=TT / ID_CATEGORIA=TT"
    )

    # --------------------------------------------------------
    # VARIABLES NUMÉRICAS
    # --------------------------------------------------------

    columnas_numericas = [
        "NUMERO_ESTABLECIMIENTOS",
        "NUMERO_HABITACIONES",
        "NUMERO_PLAZAS_CAMA",
        "PORCENTAJE_TNOH",
        "PORCENTAJE_TNOC",
        "PROMEDIO_PERMANENCIA",
        "PROMEDIO_PERMANENCIA_NAC",
        "PROMEDIO_PERMANENCIA_EXT",
        "TOTAL_ARRIBOS",
        "TOTAL_ARRIBOS_NAC",
        "TOTAL_ARRIBOS_EXT",
        "TOTAL_PERNOCT",
        "TOTAL_PERNOCT_NAC",
        "TOTAL_PERNOCT_EXT",
        "TOTAL_EMPLEO"
    ]

    for columna in columnas_numericas:

        consolidado[
            columna
        ] = convertir_numero(
            consolidado[
                columna
            ]
        )

    consolidado[
        "ANIO"
    ] = pd.to_numeric(
        consolidado[
            "ANIO"
        ],
        errors="coerce"
    )

    consolidado[
        "MES"
    ] = pd.to_numeric(
        consolidado[
            "MES"
        ],
        errors="coerce"
    )

    return consolidado


# ============================================================
# VALIDAR UNICIDAD MENSUAL
# ============================================================

def validar_unicidad(base):

    control = (
        base
        .groupby(
            [
                "Departamento_Radar",
                "ANIO",
                "MES"
            ]
        )
        .size()
        .reset_index(
            name="Registros"
        )
    )

    duplicados = control[
        control[
            "Registros"
        ] > 1
    ]

    print(
        "\n" + "=" * 100
    )

    print(
        "CONTROL DE UNICIDAD TERRITORIAL/MENSUAL"
    )

    print(
        "=" * 100
    )

    print(
        f"Combinaciones departamento-mes : "
        f"{len(control):,}"
    )

    print(
        f"Combinaciones duplicadas        : "
        f"{len(duplicados):,}"
    )

    if not duplicados.empty:

        print(
            "\n⚠ Se encontraron duplicados:"
        )

        print(
            duplicados
            .head(20)
            .to_string(
                index=False
            )
        )

    return control


# ============================================================
# RESUMEN TERRITORIAL
# ============================================================

def construir_resumen(base):

    filas = []

    for departamento, grupo in base.groupby(
        "Departamento_Radar"
    ):

        arribos = grupo[
            "TOTAL_ARRIBOS"
        ].sum(
            min_count=1
        )

        arribos_nac = grupo[
            "TOTAL_ARRIBOS_NAC"
        ].sum(
            min_count=1
        )

        arribos_ext = grupo[
            "TOTAL_ARRIBOS_EXT"
        ].sum(
            min_count=1
        )

        pernoct = grupo[
            "TOTAL_PERNOCT"
        ].sum(
            min_count=1
        )

        pernoct_nac = grupo[
            "TOTAL_PERNOCT_NAC"
        ].sum(
            min_count=1
        )

        pernoct_ext = grupo[
            "TOTAL_PERNOCT_EXT"
        ].sum(
            min_count=1
        )

        # Permanencia derivada preferida
        permanencia = (
            pernoct / arribos
            if (
                pd.notna(arribos)
                and arribos > 0
                and pd.notna(pernoct)
            )
            else pd.NA
        )

        permanencia_nac = (
            pernoct_nac / arribos_nac
            if (
                pd.notna(arribos_nac)
                and arribos_nac > 0
                and pd.notna(pernoct_nac)
            )
            else pd.NA
        )

        permanencia_ext = (
            pernoct_ext / arribos_ext
            if (
                pd.notna(arribos_ext)
                and arribos_ext > 0
                and pd.notna(pernoct_ext)
            )
            else pd.NA
        )

        # Capacidad: promedio mensual
        establecimientos = grupo[
            "NUMERO_ESTABLECIMIENTOS"
        ].mean()

        habitaciones = grupo[
            "NUMERO_HABITACIONES"
        ].mean()

        plazas_cama = grupo[
            "NUMERO_PLAZAS_CAMA"
        ].mean()

        # Ocupabilidad: promedio mensual
        tnoh = grupo[
            "PORCENTAJE_TNOH"
        ].mean()

        tnoc = grupo[
            "PORCENTAJE_TNOC"
        ].mean()

        # Empleo: promedio mensual, no suma
        empleo = grupo[
            "TOTAL_EMPLEO"
        ].mean()

        meses = grupo[
            "MES"
        ].nunique()

        filas.append(
            {
                "Departamento":
                    departamento,

                "Meses_Con_Dato":
                    meses,

                "Arribos":
                    arribos,

                "Arribos_Nacionales":
                    arribos_nac,

                "Arribos_Extranjeros":
                    arribos_ext,

                "Pernoctaciones":
                    pernoct,

                "Pernoctaciones_Nacionales":
                    pernoct_nac,

                "Pernoctaciones_Extranjeros":
                    pernoct_ext,

                "Permanencia_Promedio":
                    permanencia,

                "Permanencia_Nacionales":
                    permanencia_nac,

                "Permanencia_Extranjeros":
                    permanencia_ext,

                "TNOH_Promedio":
                    tnoh,

                "TNOC_Promedio":
                    tnoc,

                "Establecimientos_Promedio":
                    establecimientos,

                "Habitaciones_Promedio":
                    habitaciones,

                "Plazas_Cama_Promedio":
                    plazas_cama,

                "Empleo_Promedio":
                    empleo
            }
        )

    territorial = pd.DataFrame(
        filas
    )

    catalogo = pd.DataFrame(
        {
            "Departamento":
                DEPARTAMENTOS_PERU
        }
    )

    resumen = catalogo.merge(
        territorial,
        on="Departamento",
        how="left"
    )

    resumen[
        "Participacion_Arribos_Extranjeros"
    ] = (
        resumen[
            "Arribos_Extranjeros"
        ]
        / resumen[
            "Arribos"
        ].replace(
            0,
            pd.NA
        )
        * 100
    ).fillna(0)

    resumen[
        "Participacion_Pernoctaciones_Extranjeros"
    ] = (
        resumen[
            "Pernoctaciones_Extranjeros"
        ]
        / resumen[
            "Pernoctaciones"
        ].replace(
            0,
            pd.NA
        )
        * 100
    ).fillna(0)

    resumen[
        "Tiene_Dato_Hospedaje"
    ] = (
        resumen[
            "Arribos"
        ]
        .notna()
    ).astype(int)

    return resumen


# ============================================================
# CONTROL NACIONAL
# ============================================================

def calcular_control_nacional(
    resumen
):

    arribos = resumen[
        "Arribos"
    ].sum(
        min_count=1
    )

    arribos_nac = resumen[
        "Arribos_Nacionales"
    ].sum(
        min_count=1
    )

    arribos_ext = resumen[
        "Arribos_Extranjeros"
    ].sum(
        min_count=1
    )

    pernoct = resumen[
        "Pernoctaciones"
    ].sum(
        min_count=1
    )

    pernoct_nac = resumen[
        "Pernoctaciones_Nacionales"
    ].sum(
        min_count=1
    )

    pernoct_ext = resumen[
        "Pernoctaciones_Extranjeros"
    ].sum(
        min_count=1
    )

    permanencia = (
        pernoct / arribos
        if (
            pd.notna(arribos)
            and arribos > 0
        )
        else pd.NA
    )

    permanencia_nac = (
        pernoct_nac / arribos_nac
        if (
            pd.notna(arribos_nac)
            and arribos_nac > 0
        )
        else pd.NA
    )

    permanencia_ext = (
        pernoct_ext / arribos_ext
        if (
            pd.notna(arribos_ext)
            and arribos_ext > 0
        )
        else pd.NA
    )

    return {
        "Arribos":
            arribos,

        "Arribos_Nacionales":
            arribos_nac,

        "Arribos_Extranjeros":
            arribos_ext,

        "Pernoctaciones":
            pernoct,

        "Pernoctaciones_Nacionales":
            pernoct_nac,

        "Pernoctaciones_Extranjeros":
            pernoct_ext,

        "Permanencia":
            permanencia,

        "Permanencia_Nacional":
            permanencia_nac,

        "Permanencia_Extranjera":
            permanencia_ext
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 100)

    print(
        "RADAR TURISMO DE NATURALEZA "
        "Y AVENTURA - PERÚ"
    )

    print(
        "19 - HOSPEDAJE, PERMANENCIA "
        "Y OCUPABILIDAD DEFINITIVO"
    )

    print("=" * 100)

    ruta, descripcion = obtener_archivo()

    if ruta is None:

        print(
            "\nNo fue posible obtener el archivo."
        )

        print(
            "\nDescárgalo manualmente como:"
        )

        print(
            CSV_LOCAL
        )

        return

    print(
        "\nRecurso utilizado:"
    )

    print(
        descripcion
    )

    df = leer_csv_flexible(
        ruta
    )

    base = preparar_base(
        df
    )

    validar_unicidad(
        base
    )

    resumen = construir_resumen(
        base
    )

    control = calcular_control_nacional(
        resumen
    )

    # ========================================================
    # MOSTRAR RESUMEN
    # ========================================================

    print(
        "\n" + "=" * 100
    )

    print(
        "HOSPEDAJE POR TERRITORIO"
    )

    print(
        "=" * 100
    )

    print(
        resumen
        .sort_values(
            "Arribos",
            ascending=False,
            na_position="last"
        )
        .to_string(
            index=False,
            formatters={
                "Arribos":
                    lambda x:
                    f"{x:,.0f}",

                "Arribos_Nacionales":
                    lambda x:
                    f"{x:,.0f}",

                "Arribos_Extranjeros":
                    lambda x:
                    f"{x:,.0f}",

                "Pernoctaciones":
                    lambda x:
                    f"{x:,.0f}",

                "Permanencia_Promedio":
                    lambda x:
                    f"{x:.2f}",

                "Permanencia_Nacionales":
                    lambda x:
                    f"{x:.2f}",

                "Permanencia_Extranjeros":
                    lambda x:
                    f"{x:.2f}",

                "TNOH_Promedio":
                    lambda x:
                    f"{x:.1f}%",

                "TNOC_Promedio":
                    lambda x:
                    f"{x:.1f}%",

                "Participacion_Arribos_Extranjeros":
                    lambda x:
                    f"{x:.1f}%"
            }
        )
    )

    # ========================================================
    # CONTROL
    # ========================================================

    con_dato = int(
        resumen[
            "Tiene_Dato_Hospedaje"
        ].sum()
    )

    sin_dato = (
        len(resumen)
        - con_dato
    )

    meses_maximos = resumen[
        "Meses_Con_Dato"
    ].max()

    print(
        "\n" + "=" * 100
    )

    print(
        "CONTROL"
    )

    print(
        "=" * 100
    )

    print(
        f"TERRITORIOS CATÁLOGO              : "
        f"{len(resumen)}"
    )

    print(
        f"TERRITORIOS CON DATO              : "
        f"{con_dato}"
    )

    print(
        f"TERRITORIOS SIN DATO              : "
        f"{sin_dato}"
    )

    print(
        f"MÁXIMO MESES CON DATO             : "
        f"{meses_maximos:.0f}"
    )

    print(
        f"ARRIBOS TOTAL                     : "
        f"{control['Arribos']:,.0f}"
    )

    print(
        f"ARRIBOS NACIONALES                : "
        f"{control['Arribos_Nacionales']:,.0f}"
    )

    print(
        f"ARRIBOS EXTRANJEROS               : "
        f"{control['Arribos_Extranjeros']:,.0f}"
    )

    print(
        f"PERNOCTACIONES TOTAL              : "
        f"{control['Pernoctaciones']:,.0f}"
    )

    print(
        f"PERNOCTACIONES NACIONALES         : "
        f"{control['Pernoctaciones_Nacionales']:,.0f}"
    )

    print(
        f"PERNOCTACIONES EXTRANJEROS        : "
        f"{control['Pernoctaciones_Extranjeros']:,.0f}"
    )

    print(
        f"PERMANENCIA PROMEDIO              : "
        f"{control['Permanencia']:.2f} noches"
    )

    print(
        f"PERMANENCIA NACIONALES            : "
        f"{control['Permanencia_Nacional']:.2f} noches"
    )

    print(
        f"PERMANENCIA EXTRANJEROS           : "
        f"{control['Permanencia_Extranjera']:.2f} noches"
    )

    # ========================================================
    # EXPORTAR
    # ========================================================

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        resumen.to_excel(
            writer,
            sheet_name="Hospedaje_Territorial",
            index=False
        )

        base.to_excel(
            writer,
            sheet_name="Base_Consolidada",
            index=False
        )

    print(
        "\nARCHIVO GENERADO:"
    )

    print(
        SALIDA
    )

    print(
        "\n✓ CAPA DE HOSPEDAJE "
        "Y PERMANENCIA VALIDADA"
    )

    print(
        "FIN"
    )


if __name__ == "__main__":
    main()
    