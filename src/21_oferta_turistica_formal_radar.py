from pathlib import Path
import re
import unicodedata

import pandas as pd


# ============================================================
# RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ
# FASE 2
# ETAPA 21: OFERTA TURÍSTICA FORMAL
# VERSIÓN CORREGIDA DEFINITIVA
# ============================================================

CSV_HOSPEDAJES = Path(
    "data/fase2_raw/mincetur_directorio_hospedajes.csv"
)

CSV_AGENCIAS = Path(
    "data/fase2_raw/mincetur_directorio_agencias.csv"
)

CSV_RESTAURANTES = Path(
    "data/fase2_raw/mincetur_directorio_restaurantes.csv"
)

SALIDA = Path(
    "outputs/radar_fase2_oferta_turistica_formal_2026.xlsx"
)

SALIDA.parent.mkdir(
    parents=True,
    exist_ok=True
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


def normalizar_columna(valor):

    return (
        normalizar_texto(valor)
        .replace(" ", "_")
    )


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
# LECTURA ROBUSTA
# ============================================================

def leer_csv_robusto(ruta):

    if not ruta.exists():

        raise FileNotFoundError(
            f"No existe: {ruta}"
        )

    codificaciones = [
        "utf-8-sig",
        "utf-8",
        "latin1",
        "cp1252"
    ]

    ultimo_error = None

    for encoding in codificaciones:

        try:

            df = pd.read_csv(
                ruta,
                sep=";",
                encoding=encoding,
                engine="python",
                dtype=str,
                on_bad_lines="skip"
            )

            if len(df.columns) >= 3:

                print(
                    "\nCSV leído correctamente"
                )

                print(
                    f"Archivo   : {ruta.name}"
                )

                print(
                    f"Encoding  : {encoding}"
                )

                print(
                    "Separador : ';'"
                )

                print(
                    f"Registros : {len(df):,}"
                )

                print(
                    f"Columnas  : {len(df.columns)}"
                )

                return df

        except Exception as error:

            ultimo_error = error

    raise RuntimeError(
        f"No se pudo leer {ruta}. "
        f"Último error: {ultimo_error}"
    )


# ============================================================
# DETECTOR DE COLUMNAS
# ============================================================

def buscar_columna(
    columnas,
    candidatos
):

    mapa = {
        normalizar_columna(c):
            c
        for c in columnas
    }

    # coincidencia exacta
    for candidato in candidatos:

        clave = normalizar_columna(
            candidato
        )

        if clave in mapa:
            return mapa[clave]

    # coincidencia parcial
    for candidato in candidatos:

        clave = normalizar_columna(
            candidato
        )

        for normalizada, original in mapa.items():

            if (
                clave in normalizada
                or normalizada in clave
            ):

                return original

    return None


# ============================================================
# CREAR ID DE LOCAL / PRESTADOR
# ============================================================

def construir_id_local(
    base,
    col_ruc,
    col_nombre,
    col_ubigeo,
    col_direccion,
    tipo
):

    partes = []

    if col_ruc:
        partes.append(
            base[col_ruc]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    if col_nombre:
        partes.append(
            base[col_nombre]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    if col_ubigeo:
        partes.append(
            base[col_ubigeo]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    if col_direccion:
        partes.append(
            base[col_direccion]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    if partes:

        resultado = partes[0]

        for parte in partes[1:]:

            resultado = (
                resultado
                + "|"
                + parte
            )

        return resultado

    return (
        tipo
        + "_"
        + base.index.astype(str)
    )


# ============================================================
# PREPARAR BASE
# ============================================================

def preparar_base(
    df,
    tipo
):

    print(
        "\n" + "=" * 100
    )

    print(
        f"ESTRUCTURA — {tipo}"
    )

    print(
        "=" * 100
    )

    print(
        f"Registros : {len(df):,}"
    )

    print(
        f"Columnas  : {len(df.columns)}"
    )

    # --------------------------------------------------------
    # DETECTAR CAMPOS
    # --------------------------------------------------------

    col_departamento = buscar_columna(
        df.columns,
        [
            "departamento",
            "des_depa",
            "des departamento",
            "departamento establecimiento",
            "region"
        ]
    )

    col_provincia = buscar_columna(
        df.columns,
        [
            "provincia",
            "des_prov"
        ]
    )

    col_distrito = buscar_columna(
        df.columns,
        [
            "distrito",
            "des_dist"
        ]
    )

    col_ubigeo = buscar_columna(
        df.columns,
        [
            "cod_ubigeo",
            "ubigeo",
            "codigo ubigeo",
            "id ubigeo"
        ]
    )

    col_ruc = buscar_columna(
        df.columns,
        [
            "ruc",
            "numero ruc"
        ]
    )

    col_nombre = buscar_columna(
        df.columns,
        [
            "nombre comercial",
            "nombre_comercial",
            "razon social",
            "razon_social",
            "nombre establecimiento",
            "establecimiento",
            "agencia",
            "nombre"
        ]
    )

    col_direccion = buscar_columna(
        df.columns,
        [
            "direccion",
            "domicilio",
            "des_via",
            "via"
        ]
    )

    col_categoria = buscar_columna(
        df.columns,
        [
            "categoria",
            "categoría"
        ]
    )

    col_clase = buscar_columna(
        df.columns,
        [
            "clase",
            "clasificacion",
            "clasificación",
            "tipo establecimiento",
            "tipo"
        ]
    )

    col_certificado = buscar_columna(
        df.columns,
        [
            "nro certificado",
            "nro_certificado",
            "numero certificado",
            "certificado"
        ]
    )

    print(
        "\n" + "=" * 100
    )

    print(
        f"CAMPOS DETECTADOS — {tipo}"
    )

    print(
        "=" * 100
    )

    print(
        f"Departamento : {col_departamento}"
    )

    print(
        f"Provincia    : {col_provincia}"
    )

    print(
        f"Distrito     : {col_distrito}"
    )

    print(
        f"Ubigeo       : {col_ubigeo}"
    )

    print(
        f"RUC          : {col_ruc}"
    )

    print(
        f"Nombre       : {col_nombre}"
    )

    print(
        f"Dirección    : {col_direccion}"
    )

    print(
        f"Clase        : {col_clase}"
    )

    print(
        f"Categoría    : {col_categoria}"
    )

    print(
        f"Certificado  : {col_certificado}"
    )

    if not col_departamento:

        raise ValueError(
            f"No se detectó Departamento "
            f"en {tipo}"
        )

    base = df.copy()

    # --------------------------------------------------------
    # DEPARTAMENTO
    # --------------------------------------------------------

    base[
        "Departamento_Radar"
    ] = (
        base[col_departamento]
        .apply(
            homologar_departamento
        )
    )

    # --------------------------------------------------------
    # PROVINCIA / DISTRITO
    # --------------------------------------------------------

    if col_provincia:

        base[
            "Provincia_Radar"
        ] = (
            base[col_provincia]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        base[
            "Provincia_Radar"
        ] = ""

    if col_distrito:

        base[
            "Distrito_Radar"
        ] = (
            base[col_distrito]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        base[
            "Distrito_Radar"
        ] = ""

    # --------------------------------------------------------
    # NOMBRE
    # --------------------------------------------------------

    if col_nombre:

        base[
            "Nombre_Prestador_Radar"
        ] = (
            base[col_nombre]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        base[
            "Nombre_Prestador_Radar"
        ] = ""

    # --------------------------------------------------------
    # CATEGORÍA
    # --------------------------------------------------------

    if col_categoria:

        base[
            "Categoria_Radar"
        ] = (
            base[col_categoria]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        base[
            "Categoria_Radar"
        ] = ""

    # --------------------------------------------------------
    # CLASE
    # --------------------------------------------------------

    if col_clase:

        base[
            "Clase_Radar"
        ] = (
            base[col_clase]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        base[
            "Clase_Radar"
        ] = ""

    # --------------------------------------------------------
    # ID LOCAL
    # --------------------------------------------------------

    base[
        "ID_Local_Radar"
    ] = construir_id_local(
        base,
        col_ruc,
        col_nombre,
        col_ubigeo,
        col_direccion,
        tipo
    )

    base[
        "Tipo_Prestador_Radar"
    ] = tipo

    # --------------------------------------------------------
    # LIMPIAR TERRITORIOS VACÍOS
    # --------------------------------------------------------

    base = base[
        base[
            "Departamento_Radar"
        ] != ""
    ].copy()

    return base


# ============================================================
# CONTROL TERRITORIAL
# ============================================================

def control_territorial(
    base,
    tipo
):

    territorios = sorted(
        base[
            "Departamento_Radar"
        ]
        .dropna()
        .unique()
    )

    fuera_catalogo = [
        x
        for x in territorios
        if x not in DEPARTAMENTOS_PERU
    ]

    print(
        "\n" + "=" * 100
    )

    print(
        f"CONTROL TERRITORIAL — {tipo}"
    )

    print(
        "=" * 100
    )

    print(
        f"Territorios detectados : "
        f"{len(territorios)}"
    )

    print(
        f"Fuera del catálogo      : "
        f"{len(fuera_catalogo)}"
    )

    if fuera_catalogo:

        for valor in fuera_catalogo:

            print(
                f" - {valor}"
            )


# ============================================================
# CONTROL DUPLICADOS
# ============================================================

def control_duplicados(
    base,
    tipo
):

    control = (
        base
        .groupby(
            [
                "Departamento_Radar",
                "ID_Local_Radar"
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
    ].copy()

    print(
        "\n" + "=" * 100
    )

    print(
        f"CONTROL DUPLICADOS — {tipo}"
    )

    print(
        "=" * 100
    )

    print(
        f"Registros base       : "
        f"{len(base):,}"
    )

    print(
        f"Locales únicos       : "
        f"{len(control):,}"
    )

    print(
        f"IDs repetidos        : "
        f"{len(duplicados):,}"
    )

    return duplicados


# ============================================================
# CONTEO TERRITORIAL
# ============================================================

def contar_locales(
    base,
    nombre_columna
):

    if base.empty:

        return pd.DataFrame(
            columns=[
                "Departamento",
                nombre_columna
            ]
        )

    conteo = (
        base
        .drop_duplicates(
            subset=[
                "Departamento_Radar",
                "ID_Local_Radar"
            ]
        )
        .groupby(
            "Departamento_Radar",
            as_index=False
        )
        .agg(
            **{
                nombre_columna: (
                    "ID_Local_Radar",
                    "count"
                )
            }
        )
        .rename(
            columns={
                "Departamento_Radar":
                    "Departamento"
            }
        )
    )

    return conteo


# ============================================================
# CONSTRUIR RESUMEN
# ============================================================

def construir_resumen(
    hospedajes,
    agencias,
    restaurantes
):

    resumen = pd.DataFrame(
        {
            "Departamento":
                DEPARTAMENTOS_PERU
        }
    )

    h = contar_locales(
        hospedajes,
        "Hospedajes_Formales"
    )

    a = contar_locales(
        agencias,
        "Agencias_Formales"
    )

    r = contar_locales(
        restaurantes,
        "Restaurantes_Calificados"
    )

    resumen = resumen.merge(
        h,
        on="Departamento",
        how="left"
    )

    resumen = resumen.merge(
        a,
        on="Departamento",
        how="left"
    )

    resumen = resumen.merge(
        r,
        on="Departamento",
        how="left"
    )

    columnas = [
        "Hospedajes_Formales",
        "Agencias_Formales",
        "Restaurantes_Calificados"
    ]

    for columna in columnas:

        resumen[
            columna
        ] = (
            resumen[
                columna
            ]
            .fillna(0)
            .astype(int)
        )

    resumen[
        "Prestadores_Formales_Total"
    ] = (
        resumen[
            "Hospedajes_Formales"
        ]
        +
        resumen[
            "Agencias_Formales"
        ]
        +
        resumen[
            "Restaurantes_Calificados"
        ]
    )

    resumen[
        "Tiene_Oferta_Formal"
    ] = (
        resumen[
            "Prestadores_Formales_Total"
        ] > 0
    ).astype(int)

    resumen = (
        resumen
        .sort_values(
            "Prestadores_Formales_Total",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    resumen.insert(
        0,
        "Ranking_Oferta",
        range(
            1,
            len(resumen) + 1
        )
    )

    return resumen


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 100
    )

    print(
        "RADAR TURISMO NATURALEZA "
        "Y AVENTURA - PERÚ"
    )

    print(
        "21 - OFERTA TURÍSTICA FORMAL "
        "CORREGIDA"
    )

    print(
        "=" * 100
    )

    archivos = {
        "HOSPEDAJES":
            CSV_HOSPEDAJES,

        "AGENCIAS":
            CSV_AGENCIAS,

        "RESTAURANTES":
            CSV_RESTAURANTES
    }

    bases = {}

    duplicados_control = {}

    # ========================================================
    # CARGAR LAS TRES BASES
    # ========================================================

    for tipo, ruta in archivos.items():

        print(
            "\n" + "#" * 100
        )

        print(
            tipo
        )

        print(
            "#" * 100
        )

        df = leer_csv_robusto(
            ruta
        )

        base = preparar_base(
            df,
            tipo
        )

        control_territorial(
            base,
            tipo
        )

        duplicados = control_duplicados(
            base,
            tipo
        )

        bases[
            tipo
        ] = base

        duplicados_control[
            tipo
        ] = duplicados

    # ========================================================
    # RESUMEN
    # ========================================================

    resumen = construir_resumen(
        bases["HOSPEDAJES"],
        bases["AGENCIAS"],
        bases["RESTAURANTES"]
    )

    print(
        "\n" + "=" * 100
    )

    print(
        "RANKING TERRITORIAL "
        "DE OFERTA TURÍSTICA FORMAL"
    )

    print(
        "=" * 100
    )

    print(
        resumen.to_string(
            index=False
        )
    )

    # ========================================================
    # CONTROL FINAL
    # ========================================================

    total_hospedajes = resumen[
        "Hospedajes_Formales"
    ].sum()

    total_agencias = resumen[
        "Agencias_Formales"
    ].sum()

    total_restaurantes = resumen[
        "Restaurantes_Calificados"
    ].sum()

    total = resumen[
        "Prestadores_Formales_Total"
    ].sum()

    territorios = int(
        resumen[
            "Tiene_Oferta_Formal"
        ].sum()
    )

    print(
        "\n" + "=" * 100
    )

    print(
        "CONTROL FINAL"
    )

    print(
        "=" * 100
    )

    print(
        f"TERRITORIOS CATÁLOGO          : "
        f"{len(resumen)}"
    )

    print(
        f"TERRITORIOS CON OFERTA        : "
        f"{territorios}"
    )

    print(
        f"HOSPEDAJES FORMALES           : "
        f"{total_hospedajes:,}"
    )

    print(
        f"AGENCIAS FORMALES             : "
        f"{total_agencias:,}"
    )

    print(
        f"RESTAURANTES CALIFICADOS      : "
        f"{total_restaurantes:,}"
    )

    print(
        f"LOCALES/PRESTADORES TOTAL     : "
        f"{total:,}"
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
            sheet_name="Oferta_Territorial",
            index=False
        )

        bases[
            "HOSPEDAJES"
        ].to_excel(
            writer,
            sheet_name="Base_Hospedajes",
            index=False
        )

        bases[
            "AGENCIAS"
        ].to_excel(
            writer,
            sheet_name="Base_Agencias",
            index=False
        )

        bases[
            "RESTAURANTES"
        ].to_excel(
            writer,
            sheet_name="Base_Restaurantes",
            index=False
        )

        for tipo, duplicados in (
            duplicados_control.items()
        ):

            duplicados.to_excel(
                writer,
                sheet_name=(
                    "Duplicados_"
                    + tipo[:18]
                ),
                index=False
            )

    print(
        "\nARCHIVO GENERADO:"
    )

    print(
        SALIDA
    )

    print(
        "\n✓ AUDITORÍA DE OFERTA "
        "TURÍSTICA FORMAL COMPLETADA"
    )

    print(
        "FIN"
    )


if __name__ == "__main__":
    main()