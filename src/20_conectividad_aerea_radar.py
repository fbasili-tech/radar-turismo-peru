from pathlib import Path
import re
import unicodedata

import pandas as pd


# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# FASE 2
# 20 - CONECTIVIDAD AÉREA
# VERSIÓN DEFINITIVA
# ============================================================

ANIO_OBJETIVO = 2025

CSV_LOCAL = Path(
    "data/mincetur_movimiento_aeropuertos.csv"
)

CSV_DESCARGADO = Path(
    "data/fase2_raw/mincetur_movimiento_aeropuertos.csv"
)

SALIDA = Path(
    "outputs/radar_fase2_conectividad_aerea_2026.xlsx"
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


def convertir_numero(serie):

    return pd.to_numeric(
        serie
        .astype(str)
        .str.strip()
        .str.replace(",", "", regex=False),
        errors="coerce"
    )


# ============================================================
# ARCHIVO
# ============================================================

def obtener_archivo():

    if CSV_LOCAL.exists():

        print(
            "\nUsando archivo local:"
        )

        print(
            CSV_LOCAL
        )

        return CSV_LOCAL

    if CSV_DESCARGADO.exists():

        print(
            "\nUsando descarga previa:"
        )

        print(
            CSV_DESCARGADO
        )

        return CSV_DESCARGADO

    raise FileNotFoundError(
        "No se encontró la base de aeropuertos."
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

    for encoding in codificaciones:

        for separador in separadores:

            try:

                df = pd.read_csv(
                    ruta,
                    encoding=encoding,
                    sep=separador,
                    low_memory=False
                )

                if len(df.columns) >= 7:

                    print(
                        "\nCSV leído correctamente"
                    )

                    print(
                        f"Encoding : {encoding}"
                    )

                    print(
                        f"Separador: {repr(separador)}"
                    )

                    return df

            except Exception:
                continue

    raise RuntimeError(
        "No fue posible leer el CSV."
    )


# ============================================================
# PREPARAR BASE
# ============================================================

def preparar_base(df):

    requeridas = [
        "ANIO",
        "MES",
        "DEPARTAMENTO",
        "AEROPUERTO",
        "TIPO_MOVIMIENTO",
        "TIPO_VUELO",
        "NUMERO_PASAJEROS"
    ]

    faltantes = [
        c
        for c in requeridas
        if c not in df.columns
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas: "
            + ", ".join(faltantes)
        )

    base = df.copy()

    base[
        "ANIO"
    ] = pd.to_numeric(
        base["ANIO"],
        errors="coerce"
    )

    base[
        "MES"
    ] = pd.to_numeric(
        base["MES"],
        errors="coerce"
    )

    base[
        "Departamento_Radar"
    ] = (
        base["DEPARTAMENTO"]
        .apply(homologar_departamento)
    )

    base[
        "Aeropuerto_Radar"
    ] = (
        base["AEROPUERTO"]
        .astype(str)
        .str.strip()
    )

    base[
        "Movimiento_Radar"
    ] = (
        base["TIPO_MOVIMIENTO"]
        .apply(normalizar_texto)
    )

    base[
        "Tipo_Vuelo_Radar"
    ] = (
        base["TIPO_VUELO"]
        .apply(normalizar_texto)
    )

    base[
        "Pasajeros_Radar"
    ] = convertir_numero(
        base["NUMERO_PASAJEROS"]
    )

    base = base[
        base["ANIO"] == ANIO_OBJETIVO
    ].copy()

    return base


# ============================================================
# RESÚMENES AUXILIARES
# ============================================================

def sumar_por_departamento(
    base,
    movimiento=None,
    tipo_vuelo=None
):

    trabajo = base.copy()

    if movimiento is not None:

        trabajo = trabajo[
            trabajo[
                "Movimiento_Radar"
            ] == movimiento
        ]

    if tipo_vuelo is not None:

        trabajo = trabajo[
            trabajo[
                "Tipo_Vuelo_Radar"
            ] == tipo_vuelo
        ]

    return (
        trabajo
        .groupby(
            "Departamento_Radar"
        )[
            "Pasajeros_Radar"
        ]
        .sum()
    )


# ============================================================
# CONSTRUIR RESUMEN TERRITORIAL
# ============================================================

def construir_resumen(base):

    # --------------------------------------------------------
    # TOTAL OFICIAL:
    # SOLO MOVIMIENTO GENERAL
    # --------------------------------------------------------

    total = sumar_por_departamento(
        base,
        movimiento="MOVIMIENTO GENERAL"
    )

    domestico = sumar_por_departamento(
        base,
        movimiento="MOVIMIENTO GENERAL",
        tipo_vuelo="DOMESTICO"
    )

    internacional = sumar_por_departamento(
        base,
        movimiento="MOVIMIENTO GENERAL",
        tipo_vuelo="INTERNACIONAL"
    )

    # --------------------------------------------------------
    # INDICADORES COMPLEMENTARIOS
    # --------------------------------------------------------

    llegadas = sumar_por_departamento(
        base,
        movimiento="LLEGADAS"
    )

    salidas = sumar_por_departamento(
        base,
        movimiento="SALIDAS"
    )

    # --------------------------------------------------------
    # AEROPUERTOS
    # --------------------------------------------------------

    movimiento_general = base[
        base[
            "Movimiento_Radar"
        ] == "MOVIMIENTO GENERAL"
    ].copy()

    aeropuertos = (
        movimiento_general
        .groupby(
            "Departamento_Radar"
        )[
            "Aeropuerto_Radar"
        ]
        .nunique()
    )

    internacionales = (
        movimiento_general[
            (
                movimiento_general[
                    "Tipo_Vuelo_Radar"
                ] == "INTERNACIONAL"
            )
            &
            (
                movimiento_general[
                    "Pasajeros_Radar"
                ] > 0
            )
        ]
        .groupby(
            "Departamento_Radar"
        )[
            "Aeropuerto_Radar"
        ]
        .nunique()
    )

    # --------------------------------------------------------
    # CATÁLOGO
    # --------------------------------------------------------

    resumen = pd.DataFrame(
        {
            "Departamento":
                DEPARTAMENTOS_PERU
        }
    )

    resumen[
        "Pasajeros_Total"
    ] = (
        resumen[
            "Departamento"
        ]
        .map(total)
        .fillna(0)
    )

    resumen[
        "Pasajeros_Domesticos"
    ] = (
        resumen[
            "Departamento"
        ]
        .map(domestico)
        .fillna(0)
    )

    resumen[
        "Pasajeros_Internacionales"
    ] = (
        resumen[
            "Departamento"
        ]
        .map(internacional)
        .fillna(0)
    )

    resumen[
        "Llegadas"
    ] = (
        resumen[
            "Departamento"
        ]
        .map(llegadas)
        .fillna(0)
    )

    resumen[
        "Salidas"
    ] = (
        resumen[
            "Departamento"
        ]
        .map(salidas)
        .fillna(0)
    )

    resumen[
        "Aeropuertos_Con_Registro"
    ] = (
        resumen[
            "Departamento"
        ]
        .map(aeropuertos)
        .fillna(0)
        .astype(int)
    )

    resumen[
        "Aeropuertos_Internacionales"
    ] = (
        resumen[
            "Departamento"
        ]
        .map(internacionales)
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # PARTICIPACIÓN INTERNACIONAL
    # --------------------------------------------------------

    resumen[
        "Participacion_Internacional_Porcentaje"
    ] = 0.0

    mascara = (
        resumen[
            "Pasajeros_Total"
        ] > 0
    )

    resumen.loc[
        mascara,
        "Participacion_Internacional_Porcentaje"
    ] = (
        resumen.loc[
            mascara,
            "Pasajeros_Internacionales"
        ]
        /
        resumen.loc[
            mascara,
            "Pasajeros_Total"
        ]
        * 100
    )

    # --------------------------------------------------------
    # INDICADORES BINARIOS
    # --------------------------------------------------------

    resumen[
        "Tiene_Conectividad_Aerea"
    ] = (
        resumen[
            "Pasajeros_Total"
        ] > 0
    ).astype(int)

    resumen[
        "Tiene_Conectividad_Internacional"
    ] = (
        resumen[
            "Pasajeros_Internacionales"
        ] > 0
    ).astype(int)

    # --------------------------------------------------------
    # CONTROL INTERNO
    # --------------------------------------------------------

    resumen[
        "Control_Llegadas_Salidas"
    ] = (
        resumen[
            "Llegadas"
        ]
        +
        resumen[
            "Salidas"
        ]
        -
        resumen[
            "Pasajeros_Total"
        ]
    )

    resumen[
        "Control_Domestico_Internacional"
    ] = (
        resumen[
            "Pasajeros_Domesticos"
        ]
        +
        resumen[
            "Pasajeros_Internacionales"
        ]
        -
        resumen[
            "Pasajeros_Total"
        ]
    )

    return resumen


# ============================================================
# RANKING AEROPUERTOS
# ============================================================

def construir_ranking_aeropuertos(base):

    trabajo = base[
        base[
            "Movimiento_Radar"
        ] == "MOVIMIENTO GENERAL"
    ].copy()

    ranking = (
        trabajo
        .groupby(
            [
                "Departamento_Radar",
                "Aeropuerto_Radar"
            ],
            as_index=False
        )
        .agg(
            Pasajeros_Total=(
                "Pasajeros_Radar",
                "sum"
            )
        )
        .rename(
            columns={
                "Departamento_Radar":
                    "Departamento",

                "Aeropuerto_Radar":
                    "Aeropuerto"
            }
        )
    )

    domestico = (
        trabajo[
            trabajo[
                "Tipo_Vuelo_Radar"
            ] == "DOMESTICO"
        ]
        .groupby(
            [
                "Departamento_Radar",
                "Aeropuerto_Radar"
            ]
        )[
            "Pasajeros_Radar"
        ]
        .sum()
    )

    internacional = (
        trabajo[
            trabajo[
                "Tipo_Vuelo_Radar"
            ] == "INTERNACIONAL"
        ]
        .groupby(
            [
                "Departamento_Radar",
                "Aeropuerto_Radar"
            ]
        )[
            "Pasajeros_Radar"
        ]
        .sum()
    )

    def buscar_serie(
        fila,
        serie
    ):

        clave = (
            fila[
                "Departamento"
            ],
            fila[
                "Aeropuerto"
            ]
        )

        return serie.get(
            clave,
            0
        )

    ranking[
        "Pasajeros_Domesticos"
    ] = ranking.apply(
        lambda fila:
        buscar_serie(
            fila,
            domestico
        ),
        axis=1
    )

    ranking[
        "Pasajeros_Internacionales"
    ] = ranking.apply(
        lambda fila:
        buscar_serie(
            fila,
            internacional
        ),
        axis=1
    )

    ranking[
        "Participacion_Internacional_Porcentaje"
    ] = 0.0

    mascara = (
        ranking[
            "Pasajeros_Total"
        ] > 0
    )

    ranking.loc[
        mascara,
        "Participacion_Internacional_Porcentaje"
    ] = (
        ranking.loc[
            mascara,
            "Pasajeros_Internacionales"
        ]
        /
        ranking.loc[
            mascara,
            "Pasajeros_Total"
        ]
        * 100
    )

    ranking = ranking.sort_values(
        "Pasajeros_Total",
        ascending=False
    )

    ranking.insert(
        0,
        "Ranking_Aeropuerto",
        range(
            1,
            len(ranking) + 1
        )
    )

    return ranking


# ============================================================
# CONTROL NACIONAL
# ============================================================

def control_nacional(resumen):

    total = resumen[
        "Pasajeros_Total"
    ].sum()

    domestico = resumen[
        "Pasajeros_Domesticos"
    ].sum()

    internacional = resumen[
        "Pasajeros_Internacionales"
    ].sum()

    llegadas = resumen[
        "Llegadas"
    ].sum()

    salidas = resumen[
        "Salidas"
    ].sum()

    diferencia_movimiento = (
        llegadas
        +
        salidas
        -
        total
    )

    diferencia_tipo_vuelo = (
        domestico
        +
        internacional
        -
        total
    )

    participacion_internacional = (
        internacional
        / total
        * 100
        if total > 0
        else 0
    )

    return {
        "Total":
            total,

        "Domestico":
            domestico,

        "Internacional":
            internacional,

        "Llegadas":
            llegadas,

        "Salidas":
            salidas,

        "Diferencia_Movimiento":
            diferencia_movimiento,

        "Diferencia_Tipo_Vuelo":
            diferencia_tipo_vuelo,

        "Participacion_Internacional":
            participacion_internacional
    }


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
        "20 - CONECTIVIDAD AÉREA "
        "DEFINITIVA"
    )

    print(
        "=" * 100
    )

    ruta = obtener_archivo()

    df = leer_csv_flexible(
        ruta
    )

    base = preparar_base(
        df
    )

    print(
        f"\nAÑO UTILIZADO              : "
        f"{ANIO_OBJETIVO}"
    )

    print(
        f"REGISTROS 2025             : "
        f"{len(base):,}"
    )

    # ========================================================
    # VALIDAR CATEGORÍAS
    # ========================================================

    movimientos = sorted(
        base[
            "Movimiento_Radar"
        ]
        .dropna()
        .unique()
    )

    vuelos = sorted(
        base[
            "Tipo_Vuelo_Radar"
        ]
        .dropna()
        .unique()
    )

    print(
        "\nMOVIMIENTOS DETECTADOS:"
    )

    for valor in movimientos:
        print(
            f" - {valor}"
        )

    print(
        "\nTIPOS DE VUELO DETECTADOS:"
    )

    for valor in vuelos:
        print(
            f" - {valor}"
        )

    # ========================================================
    # RESUMEN
    # ========================================================

    resumen = construir_resumen(
        base
    )

    ranking = (
        construir_ranking_aeropuertos(
            base
        )
    )

    control = control_nacional(
        resumen
    )

    # ========================================================
    # RANKING TERRITORIAL
    # ========================================================

    ranking_territorial = (
        resumen
        .sort_values(
            "Pasajeros_Total",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    ranking_territorial.insert(
        0,
        "Ranking_Aereo",
        range(
            1,
            len(ranking_territorial) + 1
        )
    )

    print(
        "\n" + "=" * 100
    )

    print(
        "RANKING TERRITORIAL "
        "DE CONECTIVIDAD AÉREA"
    )

    print(
        "=" * 100
    )

    columnas_mostrar = [
        "Ranking_Aereo",
        "Departamento",
        "Pasajeros_Total",
        "Pasajeros_Domesticos",
        "Pasajeros_Internacionales",
        "Participacion_Internacional_Porcentaje",
        "Aeropuertos_Con_Registro"
    ]

    print(
        ranking_territorial[
            columnas_mostrar
        ]
        .head(25)
        .to_string(
            index=False,
            formatters={
                "Pasajeros_Total":
                    lambda x:
                    f"{x:,.0f}",

                "Pasajeros_Domesticos":
                    lambda x:
                    f"{x:,.0f}",

                "Pasajeros_Internacionales":
                    lambda x:
                    f"{x:,.0f}",

                "Participacion_Internacional_Porcentaje":
                    lambda x:
                    f"{x:.1f}%"
            }
        )
    )

    # ========================================================
    # TOP AEROPUERTOS
    # ========================================================

    print(
        "\n" + "=" * 100
    )

    print(
        "TOP 15 AEROPUERTOS"
    )

    print(
        "=" * 100
    )

    print(
        ranking
        .head(15)
        .to_string(
            index=False,
            formatters={
                "Pasajeros_Total":
                    lambda x:
                    f"{x:,.0f}",

                "Pasajeros_Domesticos":
                    lambda x:
                    f"{x:,.0f}",

                "Pasajeros_Internacionales":
                    lambda x:
                    f"{x:,.0f}",

                "Participacion_Internacional_Porcentaje":
                    lambda x:
                    f"{x:.1f}%"
            }
        )
    )

    # ========================================================
    # CONTROL FINAL
    # ========================================================

    territorios_con_dato = int(
        resumen[
            "Tiene_Conectividad_Aerea"
        ].sum()
    )

    territorios_sin_dato = (
        len(resumen)
        -
        territorios_con_dato
    )

    aeropuertos = ranking[
        "Aeropuerto"
    ].nunique()

    territorios_internacionales = int(
        resumen[
            "Tiene_Conectividad_Internacional"
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
        f"AÑO UTILIZADO                       : "
        f"{ANIO_OBJETIVO}"
    )

    print(
        f"TERRITORIOS CATÁLOGO                : "
        f"{len(resumen)}"
    )

    print(
        f"TERRITORIOS CON CONECTIVIDAD        : "
        f"{territorios_con_dato}"
    )

    print(
        f"TERRITORIOS SIN CONECTIVIDAD        : "
        f"{territorios_sin_dato}"
    )

    print(
        f"TERRITORIOS CON VUELO INTERNACIONAL : "
        f"{territorios_internacionales}"
    )

    print(
        f"AEROPUERTOS CON REGISTRO            : "
        f"{aeropuertos}"
    )

    print(
        f"PASAJEROS TOTAL                     : "
        f"{control['Total']:,.0f}"
    )

    print(
        f"PASAJEROS DOMÉSTICOS                : "
        f"{control['Domestico']:,.0f}"
    )

    print(
        f"PASAJEROS INTERNACIONALES           : "
        f"{control['Internacional']:,.0f}"
    )

    print(
        f"LLEGADAS                            : "
        f"{control['Llegadas']:,.0f}"
    )

    print(
        f"SALIDAS                             : "
        f"{control['Salidas']:,.0f}"
    )

    print(
        f"PARTICIPACIÓN INTERNACIONAL         : "
        f"{control['Participacion_Internacional']:.1f}%"
    )

    print(
        f"CONTROL LLEGADAS + SALIDAS          : "
        f"{control['Diferencia_Movimiento']:,.0f}"
    )

    print(
        f"CONTROL DOMÉSTICO + INTERNACIONAL   : "
        f"{control['Diferencia_Tipo_Vuelo']:,.0f}"
    )

    # ========================================================
    # VALIDACIÓN AUTOMÁTICA
    # ========================================================

    if (
        abs(
            control[
                "Diferencia_Movimiento"
            ]
        ) < 1
        and
        abs(
            control[
                "Diferencia_Tipo_Vuelo"
            ]
        ) < 1
    ):

        estado = (
            "✓ BASE AÉREA VALIDADA"
        )

    else:

        estado = (
            "⚠ REVISAR CONTROLES "
            "DE CONSOLIDACIÓN"
        )

    print(
        "\n" + estado
    )

    # ========================================================
    # EXPORTAR
    # ========================================================

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        ranking_territorial.to_excel(
            writer,
            sheet_name="Conectividad_Territorial",
            index=False
        )

        ranking.to_excel(
            writer,
            sheet_name="Ranking_Aeropuertos",
            index=False
        )

        base.to_excel(
            writer,
            sheet_name="Base_Aerea_2025",
            index=False
        )

        control_df = pd.DataFrame(
            {
                "Indicador": [
                    "Pasajeros total",
                    "Pasajeros domésticos",
                    "Pasajeros internacionales",
                    "Llegadas",
                    "Salidas",
                    "Participación internacional %",
                    "Control llegadas + salidas",
                    "Control doméstico + internacional"
                ],

                "Valor": [
                    control["Total"],
                    control["Domestico"],
                    control["Internacional"],
                    control["Llegadas"],
                    control["Salidas"],
                    control[
                        "Participacion_Internacional"
                    ],
                    control[
                        "Diferencia_Movimiento"
                    ],
                    control[
                        "Diferencia_Tipo_Vuelo"
                    ]
                ]
            }
        )

        control_df.to_excel(
            writer,
            sheet_name="Control",
            index=False
        )

    print(
        "\nARCHIVO GENERADO:"
    )

    print(
        SALIDA
    )

    print(
        "\n✓ CAPA DE CONECTIVIDAD "
        "AÉREA COMPLETADA"
    )

    print(
        "FIN"
    )


if __name__ == "__main__":
    main()