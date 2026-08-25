from pathlib import Path
import re
import unicodedata

import numpy as np
import pandas as pd


# ============================================================
# RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ
# FASE 2
#
# 22 - CAPITAL NATURAL Y ÁREAS NATURALES PROTEGIDAS
# V5 - CONSOLIDACIÓN DEFINITIVA
# ============================================================


# ============================================================
# ARCHIVOS
# ============================================================

ENTRADA = Path(
    "data/fase2_raw/sernanp_anp.csv"
)

SALIDA = Path(
    "outputs/radar_fase2_capital_natural_anp_2026.xlsx"
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
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def homologar_departamento(valor):

    valor = normalizar_texto(
        valor
    )

    equivalencias = {
        "CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO",

        "PROVINCIA CONSTITUCIONAL CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO",

        "PROV CONST DEL CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO"
    }

    return equivalencias.get(
        valor,
        valor
    )


# ============================================================
# LECTURA
# ============================================================

def leer_base():

    if not ENTRADA.exists():

        raise FileNotFoundError(
            f"No existe: {ENTRADA}"
        )

    df = pd.read_csv(
        ENTRADA,
        sep=";",
        encoding="latin1",
        engine="python",
        dtype=str,
        on_bad_lines="skip"
    )

    print(
        f"Registros originales : {len(df):,}"
    )

    print(
        f"Columnas originales  : {len(df.columns):,}"
    )

    return df


# ============================================================
# CAMPOS OBLIGATORIOS
# ============================================================

def validar_campos(df):

    obligatorios = [
        "ANP_CODI",
        "ANP_NOMB",
        "ANP_CATE",
        "ANP_SULEG"
    ]

    faltantes = [
        c
        for c in obligatorios
        if c not in df.columns
    ]

    if faltantes:

        raise ValueError(
            "Faltan campos: "
            + ", ".join(
                faltantes
            )
        )

    departamentos = [
        c
        for c in df.columns
        if re.fullmatch(
            r"DEPARTAMENTO\d+",
            str(c).strip().upper()
        )
    ]

    departamentos = sorted(
        departamentos,
        key=lambda x: int(
            re.search(
                r"\d+",
                x
            ).group()
        )
    )

    print(
        f"Columnas territoriales: "
        f"{len(departamentos)}"
    )

    return departamentos


# ============================================================
# LIMPIEZA DE FILAS VACÍAS
# ============================================================

def limpiar_registros(df):

    trabajo = df.copy()

    trabajo[
        "ANP_CODI_LIMPIO"
    ] = (
        trabajo[
            "ANP_CODI"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    filas_vacias = trabajo[
        trabajo[
            "ANP_CODI_LIMPIO"
        ] == ""
    ].copy()

    validos = trabajo[
        trabajo[
            "ANP_CODI_LIMPIO"
        ] != ""
    ].copy()

    print(
        "\n" + "=" * 100
    )

    print(
        "CONTROL DE FILAS VACÍAS"
    )

    print(
        "=" * 100
    )

    print(
        f"Registros originales : "
        f"{len(trabajo):,}"
    )

    print(
        f"Filas sin ANP_CODI   : "
        f"{len(filas_vacias):,}"
    )

    print(
        f"Registros válidos    : "
        f"{len(validos):,}"
    )

    return (
        validos,
        filas_vacias
    )


# ============================================================
# SUPERFICIE
# ============================================================

def convertir_superficie(valor):

    if pd.isna(valor):
        return np.nan

    texto = str(valor).strip()

    if not texto:
        return np.nan

    texto = texto.replace(
        " ",
        ""
    )

    try:

        return float(
            texto
        )

    except Exception:
        pass

    try:

        return float(
            texto.replace(
                ",",
                "."
            )
        )

    except Exception:

        return np.nan


# ============================================================
# CLASIFICAR CATEGORÍA
# ============================================================

def clasificar_categoria(valor):

    texto = normalizar_texto(
        valor
    )

    if (
        "CONSERVACION PRIVADA"
        in texto
    ):

        return "ACP"

    if (
        "CONSERVACION REGIONAL"
        in texto
        or "CONSERVACON REGIONAL"
        in texto
    ):

        return "ACR"

    if (
        "ZONA RESERVADA"
        in texto
    ):

        return "ZR"

    if texto:

        return "ANP_NACIONAL"

    return "SIN CLASIFICAR"


# ============================================================
# EXTRAER TERRITORIOS
# ============================================================

def extraer_departamentos(
    grupo,
    columnas_departamento
):

    validos = set()

    invalidos = set()

    for columna in columnas_departamento:

        for valor in grupo[
            columna
        ]:

            departamento = (
                homologar_departamento(
                    valor
                )
            )

            if not departamento:

                continue

            if (
                departamento
                in DEPARTAMENTOS_PERU
            ):

                validos.add(
                    departamento
                )

            else:

                invalidos.add(
                    departamento
                )

    return (
        sorted(
            validos
        ),
        sorted(
            invalidos
        )
    )


# ============================================================
# CONSOLIDAR ANP ÚNICAS
# ============================================================

def construir_anp_unicas(
    df,
    columnas_departamento
):

    filas = []

    anomalías = []

    for codigo, grupo in df.groupby(
        "ANP_CODI_LIMPIO"
    ):

        nombres = (
            grupo[
                "ANP_NOMB"
            ]
            .dropna()
            .astype(str)
            .str.strip()
        )

        nombres = nombres[
            nombres != ""
        ]

        nombre = (
            nombres.iloc[0]
            if not nombres.empty
            else ""
        )

        categorias = (
            grupo[
                "ANP_CATE"
            ]
            .dropna()
            .astype(str)
            .str.strip()
        )

        categorias = categorias[
            categorias != ""
        ]

        categoria = (
            categorias.iloc[0]
            if not categorias.empty
            else ""
        )

        superficies = (
            grupo[
                "ANP_SULEG"
            ]
            .apply(
                convertir_superficie
            )
            .dropna()
        )

        superficie = (
            superficies.max()
            if not superficies.empty
            else np.nan
        )

        wdpaid = ""

        if (
            "ANP_WDPAID"
            in grupo.columns
        ):

            valores_wdpa = (
                grupo[
                    "ANP_WDPAID"
                ]
                .dropna()
                .astype(str)
                .str.strip()
            )

            valores_wdpa = valores_wdpa[
                valores_wdpa != ""
            ]

            if not valores_wdpa.empty:

                wdpaid = valores_wdpa.iloc[0]

        (
            departamentos,
            territorios_invalidos
        ) = extraer_departamentos(
            grupo,
            columnas_departamento
        )

        for valor in territorios_invalidos:

            anomalías.append(
                {
                    "ANP_CODI":
                        codigo,

                    "ANP_NOMB":
                        nombre,

                    "Valor_Territorial_Invalido":
                        valor
                }
            )

        n_departamentos = len(
            departamentos
        )

        superficie_atribuida = (
            superficie
            / n_departamentos
            if (
                pd.notna(
                    superficie
                )
                and n_departamentos > 0
            )
            else np.nan
        )

        filas.append(
            {
                "ANP_CODI":
                    codigo,

                "ANP_NOMB":
                    nombre,

                "ANP_CATE":
                    categoria,

                "Tipo_Capital":
                    clasificar_categoria(
                        categoria
                    ),

                "ANP_WDPAID":
                    wdpaid,

                "Superficie_Legal_Ha":
                    superficie,

                "Numero_Departamentos":
                    n_departamentos,

                "Es_Multidepartamental":
                    int(
                        n_departamentos > 1
                    ),

                "Departamentos_Unicos":
                    " | ".join(
                        departamentos
                    ),

                "Superficie_Atribuida_Referencial_Ha":
                    superficie_atribuida,

                "Registros_Origen":
                    len(
                        grupo
                    )
            }
        )

    anp_unicas = pd.DataFrame(
        filas
    )

    anomalías = pd.DataFrame(
        anomalías
    )

    return (
        anp_unicas,
        anomalías
    )


# ============================================================
# ANP SIN TERRITORIO
# ============================================================

def construir_sin_territorio(
    anp_unicas
):

    return (
        anp_unicas[
            anp_unicas[
                "Numero_Departamentos"
            ] == 0
        ]
        .copy()
        .reset_index(
            drop=True
        )
    )


# ============================================================
# ANP × TERRITORIO
# ============================================================

def construir_anp_territorio(
    anp_unicas
):

    filas = []

    for _, fila in (
        anp_unicas.iterrows()
    ):

        departamentos = [
            x.strip()
            for x in str(
                fila[
                    "Departamentos_Unicos"
                ]
            ).split("|")
            if x.strip()
        ]

        for departamento in departamentos:

            filas.append(
                {
                    "Departamento":
                        departamento,

                    "ANP_CODI":
                        fila[
                            "ANP_CODI"
                        ],

                    "ANP_NOMB":
                        fila[
                            "ANP_NOMB"
                        ],

                    "ANP_CATE":
                        fila[
                            "ANP_CATE"
                        ],

                    "Tipo_Capital":
                        fila[
                            "Tipo_Capital"
                        ],

                    "Superficie_Legal_ANP_Ha":
                        fila[
                            "Superficie_Legal_Ha"
                        ],

                    "Numero_Departamentos_ANP":
                        fila[
                            "Numero_Departamentos"
                        ],

                    "Es_Multidepartamental":
                        fila[
                            "Es_Multidepartamental"
                        ],

                    "Superficie_Atribuida_Referencial_Ha":
                        fila[
                            "Superficie_Atribuida_Referencial_Ha"
                        ]
                }
            )

    return pd.DataFrame(
        filas
    )


# ============================================================
# CAPITAL TERRITORIAL
# ============================================================

def construir_capital_territorial(
    anp_territorio
):

    catalogo = pd.DataFrame(
        {
            "Departamento":
                DEPARTAMENTOS_PERU
        }
    )

    if anp_territorio.empty:

        return catalogo

    general = (
        anp_territorio
        .groupby(
            "Departamento",
            as_index=False
        )
        .agg(
            ANP_Total=(
                "ANP_CODI",
                "nunique"
            ),

            Superficie_Atribuida_Referencial_Ha=(
                "Superficie_Atribuida_Referencial_Ha",
                "sum"
            ),

            ANP_Multidepartamentales=(
                "Es_Multidepartamental",
                "sum"
            ),

            Diversidad_Categorias=(
                "ANP_CATE",
                lambda x:
                x[
                    x.fillna("")
                    .astype(str)
                    .str.strip()
                    != ""
                ]
                .nunique()
            )
        )
    )

    tipos = (
        anp_territorio
        .pivot_table(
            index="Departamento",
            columns="Tipo_Capital",
            values="ANP_CODI",
            aggfunc=pd.Series.nunique,
            fill_value=0
        )
        .reset_index()
    )

    tipos = tipos.rename(
        columns={
            "ANP_NACIONAL":
                "ANP_Nacional",

            "ACR":
                "ACR_Total",

            "ACP":
                "ACP_Total",

            "ZR":
                "Zonas_Reservadas",

            "SIN CLASIFICAR":
                "ANP_Sin_Clasificar"
        }
    )

    resultado = (
        catalogo
        .merge(
            general,
            on="Departamento",
            how="left"
        )
        .merge(
            tipos,
            on="Departamento",
            how="left"
        )
    )

    columnas_numericas = [
        "ANP_Total",
        "Superficie_Atribuida_Referencial_Ha",
        "ANP_Multidepartamentales",
        "Diversidad_Categorias",
        "ANP_Nacional",
        "ACR_Total",
        "ACP_Total",
        "Zonas_Reservadas",
        "ANP_Sin_Clasificar"
    ]

    for columna in columnas_numericas:

        if columna not in resultado.columns:

            resultado[
                columna
            ] = 0

        resultado[
            columna
        ] = pd.to_numeric(
            resultado[
                columna
            ],
            errors="coerce"
        ).fillna(0)

    resultado[
        "Tiene_Capital_Natural"
    ] = (
        resultado[
            "ANP_Total"
        ] > 0
    ).astype(int)

    return resultado


# ============================================================
# CATEGORÍAS
# ============================================================

def construir_categorias(
    anp_unicas
):

    trabajo = (
        anp_unicas.copy()
    )

    trabajo[
        "ANP_CATE"
    ] = (
        trabajo[
            "ANP_CATE"
        ]
        .replace(
            "",
            "SIN CLASIFICAR"
        )
        .fillna(
            "SIN CLASIFICAR"
        )
    )

    return (
        trabajo
        .groupby(
            [
                "Tipo_Capital",
                "ANP_CATE"
            ],
            as_index=False
        )
        .agg(
            ANP_Unicas=(
                "ANP_CODI",
                "nunique"
            ),

            Superficie_Legal_Ha=(
                "Superficie_Legal_Ha",
                "sum"
            )
        )
        .sort_values(
            "ANP_Unicas",
            ascending=False
        )
    )


# ============================================================
# MULTIDEPARTAMENTALES
# ============================================================

def construir_multidepartamentales(
    anp_unicas
):

    return (
        anp_unicas[
            anp_unicas[
                "Es_Multidepartamental"
            ] == 1
        ]
        .copy()
        .sort_values(
            [
                "Numero_Departamentos",
                "Superficie_Legal_Ha"
            ],
            ascending=[
                False,
                False
            ]
        )
    )


# ============================================================
# DUPLICADOS DE CÓDIGO
# ============================================================

def construir_control_duplicados(
    df
):

    control = (
        df
        .groupby(
            "ANP_CODI_LIMPIO",
            as_index=False
        )
        .agg(
            Registros=(
                "ANP_CODI_LIMPIO",
                "size"
            ),

            Nombres_Distintos=(
                "ANP_NOMB",
                lambda x:
                x.fillna("")
                .astype(str)
                .str.strip()
                .nunique()
            )
        )
    )

    return control[
        (
            control[
                "Registros"
            ] > 1
        )
        |
        (
            control[
                "Nombres_Distintos"
            ] > 1
        )
    ].copy()


# ============================================================
# RESUMEN NACIONAL
# ============================================================

def construir_resumen_nacional(
    originales,
    validos,
    anp_unicas,
    anp_territorio,
    capital,
    sin_territorio,
    anomalías
):

    superficie_legal = (
        pd.to_numeric(
            anp_unicas[
                "Superficie_Legal_Ha"
            ],
            errors="coerce"
        )
        .sum()
    )

    superficie_atribuida = (
        pd.to_numeric(
            anp_territorio[
                "Superficie_Atribuida_Referencial_Ha"
            ],
            errors="coerce"
        )
        .sum()
    )

    return pd.DataFrame(
        {
            "Indicador": [
                "Registros originales SERNANP",
                "Registros válidos con código",
                "Filas vacías excluidas",
                "ANP únicas consolidadas",
                "ANP nacionales",
                "Áreas de Conservación Regional",
                "Áreas de Conservación Privada",
                "Zonas Reservadas",
                "ANP sin clasificar",
                "ANP multidepartamentales",
                "ANP sin territorio válido",
                "Valores territoriales anómalos",
                "Relaciones ANP-territorio",
                "Territorios catálogo",
                "Territorios con capital natural",
                "Superficie legal consolidada ha",
                "Superficie atribuida territorial ha",
                "Diferencia superficie ha"
            ],

            "Valor": [
                len(
                    originales
                ),

                len(
                    validos
                ),

                len(
                    originales
                )
                - len(
                    validos
                ),

                len(
                    anp_unicas
                ),

                int(
                    (
                        anp_unicas[
                            "Tipo_Capital"
                        ]
                        == "ANP_NACIONAL"
                    ).sum()
                ),

                int(
                    (
                        anp_unicas[
                            "Tipo_Capital"
                        ]
                        == "ACR"
                    ).sum()
                ),

                int(
                    (
                        anp_unicas[
                            "Tipo_Capital"
                        ]
                        == "ACP"
                    ).sum()
                ),

                int(
                    (
                        anp_unicas[
                            "Tipo_Capital"
                        ]
                        == "ZR"
                    ).sum()
                ),

                int(
                    (
                        anp_unicas[
                            "Tipo_Capital"
                        ]
                        == "SIN CLASIFICAR"
                    ).sum()
                ),

                int(
                    anp_unicas[
                        "Es_Multidepartamental"
                    ].sum()
                ),

                len(
                    sin_territorio
                ),

                len(
                    anomalías
                ),

                len(
                    anp_territorio
                ),

                len(
                    DEPARTAMENTOS_PERU
                ),

                int(
                    capital[
                        "Tiene_Capital_Natural"
                    ].sum()
                ),

                superficie_legal,

                superficie_atribuida,

                superficie_atribuida
                - superficie_legal
            ]
        }
    )


# ============================================================
# METODOLOGÍA
# ============================================================

def construir_metodologia():

    datos = [
        (
            "Fuente",
            "SERNANP - Consolidado ANP + ACR + ACP + ZR."
        ),

        (
            "Filas vacías",
            "Los registros sin ANP_CODI se excluyen porque corresponden a filas sin información de ANP."
        ),

        (
            "Identificador",
            "ANP_CODI es el identificador principal."
        ),

        (
            "Deduplicación",
            "Múltiples filas con el mismo ANP_CODI se consolidan como una sola ANP."
        ),

        (
            "Superficie",
            "ANP_SULEG se usa como superficie legal en hectáreas."
        ),

        (
            "Territorios",
            "Se revisan DEPARTAMENTO1 hasta DEPARTAMENTO30."
        ),

        (
            "Catálogo cerrado",
            "Solo se aceptan valores pertenecientes a los 25 territorios oficiales del Radar."
        ),

        (
            "Anomalías",
            "Valores como PISCO o NOMBDEP no se convierten automáticamente en departamentos."
        ),

        (
            "Repeticiones internas",
            "Un mismo departamento repetido varias veces dentro de una ANP se contabiliza solo una vez."
        ),

        (
            "Multidepartamentalidad",
            "Una ANP puede generar presencia en varios departamentos."
        ),

        (
            "Superficie referencial",
            "La superficie legal se divide en partes iguales entre departamentos únicos cuando no existe intersección GIS."
        ),

        (
            "Advertencia superficie",
            "La superficie atribuida es referencial y no sustituye una intersección geoespacial exacta."
        ),

        (
            "Pesos",
            "Esta etapa no asigna ponderaciones normativas a las categorías de conservación."
        )
    ]

    return pd.DataFrame(
        datos,
        columns=[
            "Tema",
            "Criterio_Metodologico"
        ]
    )


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
        "22 - CAPITAL NATURAL "
        "Y ÁREAS NATURALES PROTEGIDAS V5"
    )

    print(
        "=" * 100
    )

    originales = leer_base()

    columnas_departamento = (
        validar_campos(
            originales
        )
    )

    validos, filas_vacias = (
        limpiar_registros(
            originales
        )
    )

    print(
        "\nConsolidando ANP..."
    )

    (
        anp_unicas,
        anomalías
    ) = construir_anp_unicas(
        validos,
        columnas_departamento
    )

    sin_territorio = (
        construir_sin_territorio(
            anp_unicas
        )
    )

    anp_territorio = (
        construir_anp_territorio(
            anp_unicas
        )
    )

    capital = (
        construir_capital_territorial(
            anp_territorio
        )
    )

    categorias = (
        construir_categorias(
            anp_unicas
        )
    )

    multidepartamentales = (
        construir_multidepartamentales(
            anp_unicas
        )
    )

    duplicados = (
        construir_control_duplicados(
            validos
        )
    )

    resumen = construir_resumen_nacional(
        originales,
        validos,
        anp_unicas,
        anp_territorio,
        capital,
        sin_territorio,
        anomalías
    )

    metodologia = construir_metodologia()

    # ========================================================
    # EXPORTAR
    # ========================================================

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        resumen.to_excel(
            writer,
            sheet_name="01_Resumen_Nacional",
            index=False
        )

        capital.to_excel(
            writer,
            sheet_name="02_Capital_Territorial",
            index=False
        )

        anp_unicas.to_excel(
            writer,
            sheet_name="03_ANP_Unicas",
            index=False
        )

        anp_territorio.to_excel(
            writer,
            sheet_name="04_ANP_Territorio",
            index=False
        )

        categorias.to_excel(
            writer,
            sheet_name="05_Categorias",
            index=False
        )

        multidepartamentales.to_excel(
            writer,
            sheet_name="06_Multidepartamentales",
            index=False
        )

        duplicados.to_excel(
            writer,
            sheet_name="07_Control_Duplicados",
            index=False
        )

        sin_territorio.to_excel(
            writer,
            sheet_name="08_ANP_Sin_Territorio",
            index=False
        )

        anomalías.to_excel(
            writer,
            sheet_name="09_Anomalias_Territorio",
            index=False
        )

        filas_vacias.to_excel(
            writer,
            sheet_name="10_Filas_Excluidas",
            index=False
        )

        metodologia.to_excel(
            writer,
            sheet_name="11_Metodologia",
            index=False
        )

    # ========================================================
    # CONTROL FINAL
    # ========================================================

    superficie_legal = pd.to_numeric(
        anp_unicas[
            "Superficie_Legal_Ha"
        ],
        errors="coerce"
    ).sum()

    superficie_atribuida = pd.to_numeric(
        anp_territorio[
            "Superficie_Atribuida_Referencial_Ha"
        ],
        errors="coerce"
    ).sum()

    diferencia = (
        superficie_atribuida
        - superficie_legal
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
        f"REGISTROS ORIGINALES       : "
        f"{len(originales):,}"
    )

    print(
        f"FILAS VACÍAS EXCLUIDAS     : "
        f"{len(filas_vacias):,}"
    )

    print(
        f"REGISTROS VÁLIDOS          : "
        f"{len(validos):,}"
    )

    print(
        f"ANP ÚNICAS CONSOLIDADAS    : "
        f"{len(anp_unicas):,}"
    )

    print(
        f"RELACIONES ANP-TERRITORIO  : "
        f"{len(anp_territorio):,}"
    )

    print(
        f"ANP MULTIDEPARTAMENTALES   : "
        f"{anp_unicas['Es_Multidepartamental'].sum():,.0f}"
    )

    print(
        f"ANP SIN TERRITORIO VÁLIDO  : "
        f"{len(sin_territorio):,}"
    )

    print(
        f"ANOMALÍAS TERRITORIALES    : "
        f"{len(anomalías):,}"
    )

    print(
        f"TERRITORIOS CON CAPITAL    : "
        f"{capital['Tiene_Capital_Natural'].sum():,.0f}"
    )

    print(
        f"SUPERFICIE LEGAL           : "
        f"{superficie_legal:,.2f} ha"
    )

    print(
        f"SUPERFICIE ATRIBUIDA       : "
        f"{superficie_atribuida:,.2f} ha"
    )

    print(
        f"DIFERENCIA CONTROL         : "
        f"{diferencia:,.6f} ha"
    )

    print(
        "\nTIPOS DE CAPITAL:"
    )

    print(
        anp_unicas[
            "Tipo_Capital"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    print(
        "\nANOMALÍAS TERRITORIALES:"
    )

    if anomalías.empty:

        print(
            "NINGUNA"
        )

    else:

        print(
            anomalías.to_string(
                index=False
            )
        )

    print(
        "\nTOP 10 TERRITORIOS POR CAPITAL NATURAL:"
    )

    print(
        capital[
            [
                "Departamento",
                "ANP_Total",
                "ANP_Nacional",
                "ACR_Total",
                "ACP_Total",
                "Zonas_Reservadas",
                "Superficie_Atribuida_Referencial_Ha"
            ]
        ]
        .sort_values(
            [
                "ANP_Total",
                "Superficie_Atribuida_Referencial_Ha"
            ],
            ascending=[
                False,
                False
            ]
        )
        .head(10)
        .to_string(
            index=False
        )
    )

    print(
        "\nARCHIVO GENERADO:"
    )

    print(
        SALIDA
    )

    print(
        "\n✓ CAPA DE CAPITAL "
        "NATURAL V5 COMPLETADA"
    )

    print(
        "FIN"
    )


if __name__ == "__main__":
    main()