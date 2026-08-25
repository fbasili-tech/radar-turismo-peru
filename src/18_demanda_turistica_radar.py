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
# ETAPA 18: DEMANDA TURÍSTICA
# VERSIÓN CORREGIDA
# ============================================================

ANIO_OBJETIVO = 2026

CARPETA_DATA = Path("data")
CARPETA_RAW = Path("data/fase2_raw")
CARPETA_OUTPUTS = Path("outputs")

CARPETA_DATA.mkdir(
    parents=True,
    exist_ok=True
)

CARPETA_RAW.mkdir(
    parents=True,
    exist_ok=True
)

CARPETA_OUTPUTS.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# FUENTE OFICIAL
# ============================================================

URL_DATASET_VISITANTES = (
    "https://www.datosabiertos.gob.pe/dataset/"
    "visitantes-sitios-tur%C3%ADsticos-del-per%C3%BA-"
    "ministerio-de-comercio-exterior-y-turismo-mincetur"
)


# ============================================================
# ARCHIVOS
# ============================================================

CSV_LOCAL_VISITANTES = Path(
    "data/mincetur_visitantes_sitios.csv"
)

CSV_DESCARGADO_VISITANTES = Path(
    "data/fase2_raw/mincetur_visitantes_sitios.csv"
)

SALIDA = Path(
    "outputs/radar_fase2_demanda_turistica_2026.xlsx"
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


def normalizar_columna(nombre):

    return normalizar_texto(
        nombre
    ).replace(
        " ",
        "_"
    )


def homologar_departamento(valor):

    valor = normalizar_texto(
        valor
    )

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
# SESIÓN WEB
# ============================================================

def crear_sesion():

    sesion = requests.Session()

    sesion.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/151 Safari/537.36"
            ),
            "Accept":
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":
                "es-PE,es;q=0.9,en;q=0.8"
        }
    )

    return sesion


# ============================================================
# DESCUBRIR CSV
# ============================================================

def descubrir_csv_dataset(url_dataset):

    print("\nBuscando recurso CSV oficial...")

    sesion = crear_sesion()

    try:

        respuesta = sesion.get(
            url_dataset,
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
                href
                + " "
                + texto
            ).lower()

            if ".csv" in combinado:

                candidatos.append(
                    urljoin(
                        url_dataset,
                        href
                    )
                )

        if not candidatos:

            recursos = []

            for enlace in soup.find_all(
                "a",
                href=True
            ):

                href = enlace[
                    "href"
                ]

                if "/resource/" in href:

                    recursos.append(
                        urljoin(
                            url_dataset,
                            href
                        )
                    )

            recursos = list(
                dict.fromkeys(
                    recursos
                )
            )

            for recurso in recursos:

                try:

                    r = sesion.get(
                        recurso,
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

                        texto = enlace.get_text(
                            " ",
                            strip=True
                        )

                        combinado = (
                            href
                            + " "
                            + texto
                        ).lower()

                        if (
                            ".csv" in combinado
                            or "descargar" in combinado
                        ):

                            candidatos.append(
                                urljoin(
                                    recurso,
                                    href
                                )
                            )

                except Exception:
                    continue

        candidatos = list(
            dict.fromkeys(
                candidatos
            )
        )

        if not candidatos:

            print(
                "No se encontró automáticamente "
                "un enlace CSV."
            )

            return None

        candidatos.sort(
            key=lambda x: (
                ".csv" not in x.lower(),
                "download" not in x.lower()
            )
        )

        print(
            f"Recursos candidatos encontrados: "
            f"{len(candidatos)}"
        )

        return candidatos[0]

    except Exception as error:

        print(
            f"No fue posible consultar "
            f"el catálogo oficial: {error}"
        )

        return None


# ============================================================
# DESCARGAR CSV
# ============================================================

def descargar_csv(
    url,
    destino
):

    sesion = crear_sesion()

    print(
        "\nDescargando recurso oficial..."
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
            :200
        ].lower()

        if (
            b"<html" in inicio
            or b"<!doctype" in inicio
        ):

            print(
                "El recurso recibido parece HTML "
                "y no un CSV."
            )

            return False

        destino.write_bytes(
            contenido
        )

        print(
            f"Archivo descargado:\n"
            f"{destino}"
        )

        return True

    except Exception as error:

        print(
            f"Error descargando CSV: "
            f"{error}"
        )

        return False


# ============================================================
# OBTENER BASE
# ============================================================

def obtener_base_visitantes():

    if CSV_LOCAL_VISITANTES.exists():

        print(
            "\nUsando archivo local:"
        )

        print(
            CSV_LOCAL_VISITANTES
        )

        return CSV_LOCAL_VISITANTES

    if CSV_DESCARGADO_VISITANTES.exists():

        print(
            "\nUsando descarga previa:"
        )

        print(
            CSV_DESCARGADO_VISITANTES
        )

        return CSV_DESCARGADO_VISITANTES

    url_csv = descubrir_csv_dataset(
        URL_DATASET_VISITANTES
    )

    if url_csv:

        exito = descargar_csv(
            url_csv,
            CSV_DESCARGADO_VISITANTES
        )

        if exito:
            return CSV_DESCARGADO_VISITANTES

    return None


# ============================================================
# LEER CSV FLEXIBLE
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

    mejor_df = None

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
                    mejor_df is None
                    or len(
                        df.columns
                    ) > len(
                        mejor_df.columns
                    )
                ):

                    mejor_df = df

                if len(
                    df.columns
                ) >= 4:

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

    if mejor_df is not None:
        return mejor_df

    raise RuntimeError(
        "No fue posible leer el CSV."
    )


# ============================================================
# BUSCAR COLUMNAS
# ============================================================

def buscar_columna(
    columnas,
    candidatos
):

    mapa = {
        normalizar_columna(
            columna
        ): columna
        for columna in columnas
    }

    for candidato in candidatos:

        c = normalizar_columna(
            candidato
        )

        if c in mapa:
            return mapa[c]

    for candidato in candidatos:

        c = normalizar_columna(
            candidato
        )

        for normalizada, original in mapa.items():

            if (
                c in normalizada
                or normalizada in c
            ):

                return original

    return None


# ============================================================
# CONVERTIR NÚMEROS
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
            " ",
            "",
            regex=False
        )
    )

    return pd.to_numeric(
        texto,
        errors="coerce"
    ).fillna(0)


# ============================================================
# PREPARAR BASE
# ============================================================

def preparar_visitantes(df):

    print(
        "\n" + "=" * 100
    )

    print(
        "ESTRUCTURA DE LA BASE OFICIAL"
    )

    print(
        "=" * 100
    )

    print(
        f"Registros: {len(df):,}"
    )

    print(
        f"Columnas : {len(df.columns)}"
    )

    col_departamento = buscar_columna(
        df.columns,
        [
            "departamento",
            "departamento sitio",
            "region"
        ]
    )

    col_periodo = buscar_columna(
        df.columns,
        [
            "periodo",
            "fecha",
            "mes",
            "anio_mes"
        ]
    )

    col_anio = buscar_columna(
        df.columns,
        [
            "anio",
            "año"
        ]
    )

    col_sitio = buscar_columna(
        df.columns,
        [
            "sitio turistico",
            "sitio",
            "recurso turistico",
            "atractivo"
        ]
    )

    col_tipo = buscar_columna(
        df.columns,
        [
            "tipo visitante",
            "tipo de visitante",
            "procedencia",
            "nacional extranjero"
        ]
    )

    col_visitantes = buscar_columna(
        df.columns,
        [
            "visitantes",
            "cantidad visitantes",
            "numero visitantes",
            "total visitantes",
            "valor"
        ]
    )

    print(
        "\n" + "=" * 100
    )

    print(
        "CAMPOS DETECTADOS"
    )

    print(
        "=" * 100
    )

    print(
        f"Departamento : {col_departamento}"
    )

    print(
        f"Periodo      : {col_periodo}"
    )

    print(
        f"Año          : {col_anio}"
    )

    print(
        f"Sitio        : {col_sitio}"
    )

    print(
        f"Tipo visitante: {col_tipo}"
    )

    print(
        f"Visitantes   : {col_visitantes}"
    )

    if not col_departamento:
        raise ValueError(
            "No se pudo identificar Departamento."
        )

    if not col_visitantes:
        raise ValueError(
            "No se pudo identificar Visitantes."
        )

    base = df.copy()

    base[
        "Departamento_Radar"
    ] = (
        base[
            col_departamento
        ]
        .apply(
            homologar_departamento
        )
    )

    base[
        "Visitantes_Radar"
    ] = convertir_numero(
        base[
            col_visitantes
        ]
    )

    if col_anio:

        base[
            "Anio_Radar"
        ] = pd.to_numeric(
            base[
                col_anio
            ],
            errors="coerce"
        )

    elif col_periodo:

        texto_periodo = (
            base[
                col_periodo
            ]
            .astype(str)
        )

        base[
            "Anio_Radar"
        ] = pd.to_numeric(
            texto_periodo.str.extract(
                r"(20\d{2})",
                expand=False
            ),
            errors="coerce"
        )

    else:

        base[
            "Anio_Radar"
        ] = pd.NA

    if col_sitio:

        base[
            "Sitio_Radar"
        ] = (
            base[
                col_sitio
            ]
            .astype(str)
            .str.strip()
        )

    else:

        base[
            "Sitio_Radar"
        ] = ""

    if col_tipo:

        base[
            "Tipo_Visitante_Radar"
        ] = (
            base[
                col_tipo
            ]
            .apply(
                normalizar_texto
            )
        )

    else:

        base[
            "Tipo_Visitante_Radar"
        ] = "TOTAL"

    return base


# ============================================================
# CONSTRUIR RESUMEN
# ============================================================

def construir_resumen(base):

    anios_disponibles = sorted(
        [
            int(x)
            for x in base[
                "Anio_Radar"
            ].dropna().unique()
        ]
    )

    print(
        "\nAños disponibles:"
    )

    print(
        anios_disponibles
    )

    if (
        ANIO_OBJETIVO
        in anios_disponibles
    ):

        anio_usado = (
            ANIO_OBJETIVO
        )

    elif anios_disponibles:

        anio_usado = max(
            anios_disponibles
        )

        print(
            f"\n⚠ No existen registros "
            f"{ANIO_OBJETIVO}."
        )

        print(
            f"Se utilizará el último año "
            f"disponible: {anio_usado}"
        )

    else:

        anio_usado = None

    if anio_usado:

        trabajo = base[
            base[
                "Anio_Radar"
            ]
            == anio_usado
        ].copy()

    else:

        trabajo = base.copy()

    # ========================================================
    # TOTAL OFICIAL
    # ========================================================

    total_oficial = trabajo[
        trabajo[
            "Tipo_Visitante_Radar"
        ]
        == "TOTAL"
    ].copy()

    total = (
        total_oficial
        .groupby(
            "Departamento_Radar",
            as_index=False
        )
        .agg(
            Visitantes_Sitios=(
                "Visitantes_Radar",
                "sum"
            ),
            Sitios_Con_Registro=(
                "Sitio_Radar",
                lambda x:
                x[
                    x != ""
                ].nunique()
            )
        )
    )

    # ========================================================
    # NACIONALES
    # ========================================================

    nacionales = trabajo[
        trabajo[
            "Tipo_Visitante_Radar"
        ]
        == "NACIONAL"
    ]

    nac = (
        nacionales
        .groupby(
            "Departamento_Radar",
            as_index=False
        )
        .agg(
            Visitantes_Nacionales=(
                "Visitantes_Radar",
                "sum"
            )
        )
    )

    # ========================================================
    # EXTRANJEROS
    # ========================================================

    extranjeros = trabajo[
        trabajo[
            "Tipo_Visitante_Radar"
        ]
        == "EXTRANJERO"
    ]

    ext = (
        extranjeros
        .groupby(
            "Departamento_Radar",
            as_index=False
        )
        .agg(
            Visitantes_Extranjeros=(
                "Visitantes_Radar",
                "sum"
            )
        )
    )

    # ========================================================
    # CATÁLOGO 25
    # ========================================================

    catalogo = pd.DataFrame(
        {
            "Departamento":
                DEPARTAMENTOS_PERU
        }
    )

    resumen = catalogo.merge(
        total,
        left_on="Departamento",
        right_on="Departamento_Radar",
        how="left"
    )

    resumen = resumen.drop(
        columns=[
            "Departamento_Radar"
        ],
        errors="ignore"
    )

    resumen = resumen.merge(
        nac,
        left_on="Departamento",
        right_on="Departamento_Radar",
        how="left"
    )

    resumen = resumen.drop(
        columns=[
            "Departamento_Radar"
        ],
        errors="ignore"
    )

    resumen = resumen.merge(
        ext,
        left_on="Departamento",
        right_on="Departamento_Radar",
        how="left"
    )

    resumen = resumen.drop(
        columns=[
            "Departamento_Radar"
        ],
        errors="ignore"
    )

    columnas_numericas = [
        "Visitantes_Sitios",
        "Visitantes_Nacionales",
        "Visitantes_Extranjeros",
        "Sitios_Con_Registro"
    ]

    for columna in columnas_numericas:

        resumen[
            columna
        ] = (
            resumen[
                columna
            ]
            .fillna(0)
        )

    resumen[
        "Visitantes_Desagregados"
    ] = (
        resumen[
            "Visitantes_Nacionales"
        ]
        + resumen[
            "Visitantes_Extranjeros"
        ]
    )

    resumen[
        "Diferencia_Total_Desagregacion"
    ] = (
        resumen[
            "Visitantes_Sitios"
        ]
        - resumen[
            "Visitantes_Desagregados"
        ]
    )

    resumen[
        "Cobertura_Desagregacion_Porcentaje"
    ] = (
        resumen[
            "Visitantes_Desagregados"
        ]
        / resumen[
            "Visitantes_Sitios"
        ].replace(
            0,
            pd.NA
        )
        * 100
    ).fillna(0)

    resumen[
        "Participacion_Extranjera_Porcentaje"
    ] = (
        resumen[
            "Visitantes_Extranjeros"
        ]
        / resumen[
            "Visitantes_Desagregados"
        ].replace(
            0,
            pd.NA
        )
        * 100
    ).fillna(0)

    resumen[
        "Participacion_Nacional_Porcentaje"
    ] = (
        resumen[
            "Visitantes_Nacionales"
        ]
        / resumen[
            "Visitantes_Desagregados"
        ].replace(
            0,
            pd.NA
        )
        * 100
    ).fillna(0)

    resumen[
        "Anio_Demanda"
    ] = anio_usado

    resumen[
        "Tiene_Dato_Visitacion"
    ] = (
        resumen[
            "Visitantes_Sitios"
        ] > 0
    ).astype(int)

    return (
        trabajo,
        resumen,
        anio_usado
    )


# ============================================================
# TOP SITIOS
# ============================================================

def construir_top_sitios(trabajo):

    sitios = trabajo[
        (
            trabajo[
                "Sitio_Radar"
            ]
            != ""
        )
        &
        (
            trabajo[
                "Tipo_Visitante_Radar"
            ]
            == "TOTAL"
        )
    ].copy()

    if sitios.empty:

        return pd.DataFrame(
            columns=[
                "Departamento",
                "Sitio",
                "Visitantes"
            ]
        )

    top = (
        sitios
        .groupby(
            [
                "Departamento_Radar",
                "Sitio_Radar"
            ],
            as_index=False
        )
        .agg(
            Visitantes=(
                "Visitantes_Radar",
                "sum"
            )
        )
        .rename(
            columns={
                "Departamento_Radar":
                    "Departamento",
                "Sitio_Radar":
                    "Sitio"
            }
        )
        .sort_values(
            "Visitantes",
            ascending=False
        )
    )

    return top


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
        "18 - DEMANDA TURÍSTICA CORREGIDA"
    )
    print("=" * 100)

    ruta = obtener_base_visitantes()

    if ruta is None:

        print(
            "\nNo fue posible descargar "
            "automáticamente el CSV."
        )

        print(
            "\nGuárdalo manualmente como:"
        )

        print(
            CSV_LOCAL_VISITANTES
        )

        return

    df = leer_csv_flexible(
        ruta
    )

    base = preparar_visitantes(
        df
    )

    trabajo, resumen, anio = (
        construir_resumen(
            base
        )
    )

    top_sitios = construir_top_sitios(
        trabajo
    )

    # ========================================================
    # CONTROL
    # ========================================================

    con_dato = int(
        resumen[
            "Tiene_Dato_Visitacion"
        ].sum()
    )

    sin_dato = (
        len(
            resumen
        )
        - con_dato
    )

    total_visitantes = resumen[
        "Visitantes_Sitios"
    ].sum()

    total_nacionales = resumen[
        "Visitantes_Nacionales"
    ].sum()

    total_extranjeros = resumen[
        "Visitantes_Extranjeros"
    ].sum()

    total_desagregado = (
        total_nacionales
        + total_extranjeros
    )

    diferencia = (
        total_visitantes
        - total_desagregado
    )

    cobertura = (
        total_desagregado
        / total_visitantes
        * 100
        if total_visitantes > 0
        else 0
    )

    participacion_ext = (
        total_extranjeros
        / total_desagregado
        * 100
        if total_desagregado > 0
        else 0
    )

    # ========================================================
    # RESULTADOS
    # ========================================================

    print(
        "\n" + "=" * 100
    )

    print(
        "DEMANDA TERRITORIAL"
    )

    print(
        "=" * 100
    )

    print(
        resumen
        .sort_values(
            "Visitantes_Sitios",
            ascending=False
        )
        .to_string(
            index=False,
            formatters={
                "Visitantes_Sitios":
                    lambda x:
                    f"{x:,.0f}",

                "Visitantes_Nacionales":
                    lambda x:
                    f"{x:,.0f}",

                "Visitantes_Extranjeros":
                    lambda x:
                    f"{x:,.0f}",

                "Visitantes_Desagregados":
                    lambda x:
                    f"{x:,.0f}",

                "Cobertura_Desagregacion_Porcentaje":
                    lambda x:
                    f"{x:.1f}%",

                "Participacion_Extranjera_Porcentaje":
                    lambda x:
                    f"{x:.1f}%",

                "Participacion_Nacional_Porcentaje":
                    lambda x:
                    f"{x:.1f}%"
            }
        )
    )

    print(
        "\n" + "=" * 100
    )

    print(
        "TOP 20 SITIOS TURÍSTICOS"
    )

    print(
        "=" * 100
    )

    print(
        top_sitios
        .head(20)
        .to_string(
            index=False,
            formatters={
                "Visitantes":
                    lambda x:
                    f"{x:,.0f}"
            }
        )
    )

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
        f"AÑO UTILIZADO                 : "
        f"{anio}"
    )

    print(
        f"TERRITORIOS CATÁLOGO          : "
        f"{len(resumen)}"
    )

    print(
        f"TERRITORIOS CON DATO          : "
        f"{con_dato}"
    )

    print(
        f"TERRITORIOS SIN DATO          : "
        f"{sin_dato}"
    )

    print(
        f"VISITANTES TOTAL OFICIAL      : "
        f"{total_visitantes:,.0f}"
    )

    print(
        f"VISITANTES NACIONALES         : "
        f"{total_nacionales:,.0f}"
    )

    print(
        f"VISITANTES EXTRANJEROS        : "
        f"{total_extranjeros:,.0f}"
    )

    print(
        f"VISITANTES DESAGREGADOS       : "
        f"{total_desagregado:,.0f}"
    )

    print(
        f"DIFERENCIA TOTAL/DESAGREGADO  : "
        f"{diferencia:,.0f}"
    )

    print(
        f"COBERTURA DESAGREGACIÓN       : "
        f"{cobertura:.1f}%"
    )

    print(
        f"PARTICIPACIÓN EXTRANJERA      : "
        f"{participacion_ext:.1f}%"
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
            sheet_name="Demanda_Territorial",
            index=False
        )

        top_sitios.to_excel(
            writer,
            sheet_name="Ranking_Sitios",
            index=False
        )

        trabajo.to_excel(
            writer,
            sheet_name="Base_Visitantes",
            index=False
        )

    print(
        "\nARCHIVO GENERADO:"
    )

    print(
        SALIDA
    )

    print(
        "\n✓ CAPA DE DEMANDA "
        "TURÍSTICA CORREGIDA"
    )

    print(
        "FIN"
    )


if __name__ == "__main__":
    main()