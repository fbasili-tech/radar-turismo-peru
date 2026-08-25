from pathlib import Path
import json
import unicodedata
import re

import pandas as pd
import plotly.express as px


# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 15B: MAPA SEMÁFORO TERRITORIAL
# ============================================================

ENTRADA = Path(
    "outputs/radar_turismo_tablero_base_2026.xlsx"
)

GEOJSON_LOCAL = Path(
    "data/peru_departamentos.geojson"
)

SALIDA = Path(
    "outputs/mapa_semaforo_irna_peru_2026.html"
)

SALIDA_DATOS = Path(
    "outputs/radar_semaforo_territorial_2026.xlsx"
)


# ============================================================
# NORMALIZACIÓN
# ============================================================

def normalizar(texto):

    if pd.isna(texto):
        return ""

    texto = str(texto).upper().strip()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

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


def homologar(nombre):

    nombre = normalizar(nombre)

    equivalencias = {
        "PROVINCIA CONSTITUCIONAL DEL CALLAO": "CALLAO",
        "CALLAO": "CALLAO"
    }

    return equivalencias.get(
        nombre,
        nombre
    )


# ============================================================
# ESTADO EJECUTIVO
# ============================================================

def estado_semaforo(row):

    if pd.isna(
        row["IRNA_Estructural"]
    ):
        return "SIN EVIDENCIA RADAR"

    estructural = row[
        "IRNA_Estructural"
    ]

    ejecucion = row[
        "IRNA_Ejecucion"
    ]

    brecha = row[
        "Brecha_IRNA"
    ]

    # Rojo
    if brecha >= 30:
        return "BRECHA CRÍTICA"

    # Naranja
    if (
        estructural >= 60
        and ejecucion < 60
    ):
        return "REQUIERE ACELERACIÓN"

    if brecha >= 15:
        return "REQUIERE ACELERACIÓN"

    # Verde
    if (
        estructural >= 60
        and ejecucion >= 60
    ):
        return "FORTALEZA CONSOLIDADA"

    if ejecucion >= 60:
        return "BUENA EJECUCIÓN"

    # Amarillo
    return "EN CONSOLIDACIÓN"


# ============================================================
# RECOMENDACIÓN
# ============================================================

def recomendacion(row):

    estado = row[
        "Estado_Semaforo"
    ]

    if estado == "BRECHA CRÍTICA":
        return (
            "Priorizar destrabe de inversiones, "
            "seguimiento de ejecución y gestión de proyectos."
        )

    if estado == "REQUIERE ACELERACIÓN":
        return (
            "Acelerar ejecución y fortalecer la cartera "
            "de productos de naturaleza y aventura."
        )

    if estado == "FORTALEZA CONSOLIDADA":
        return (
            "Consolidar producto, promoción y articulación "
            "público-privada."
        )

    if estado == "BUENA EJECUCIÓN":
        return (
            "Ampliar masa crítica de proyectos y fortalecer "
            "la diversificación territorial."
        )

    if estado == "EN CONSOLIDACIÓN":
        return (
            "Fortalecer productos, articulación territorial "
            "y calidad de la cartera."
        )

    return (
        "Generar evidencia y desarrollar una cartera inicial "
        "de inversión vinculada a naturaleza y aventura."
    )


# ============================================================
# CARGAR GEOJSON
# ============================================================

def cargar_geojson():

    if not GEOJSON_LOCAL.exists():

        raise FileNotFoundError(
            "No se encontró data/peru_departamentos.geojson. "
            "Ejecuta primero el script 15."
        )

    with open(
        GEOJSON_LOCAL,
        "r",
        encoding="utf-8"
    ) as archivo:

        geojson = json.load(
            archivo
        )

    return geojson


# ============================================================
# DETECTAR CAMPO DEPARTAMENTO
# ============================================================

def detectar_campo(geojson):

    propiedades = (
        geojson["features"][0]
        .get(
            "properties",
            {}
        )
    )

    candidatos = [
        "DEP_RADAR",
        "NOMBDEP",
        "NOMB_DEPA",
        "DEPARTAMEN",
        "DEPARTAMENTO",
        "departamento",
        "NAME_1",
        "name",
        "NOMBRE"
    ]

    for campo in candidatos:

        if campo in propiedades:
            return campo

    raise ValueError(
        "No se pudo detectar el campo "
        "del nombre departamental."
    )


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():

    print("=" * 100)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("15B - MAPA SEMÁFORO TERRITORIAL")
    print("=" * 100)

    # --------------------------------------------------------
    # CARGAR TABLERO
    # --------------------------------------------------------

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Ranking_Nacional"
    )

    print(
        f"\nTerritorios Radar cargados: {len(df)}"
    )

    df[
        "Departamento_Mapa"
    ] = (
        df["Departamento"]
        .apply(homologar)
    )

    # --------------------------------------------------------
    # GEOJSON
    # --------------------------------------------------------

    geojson = cargar_geojson()

    campo = detectar_campo(
        geojson
    )

    # --------------------------------------------------------
    # CREAR CATÁLOGO DE LOS 25 TERRITORIOS
    # --------------------------------------------------------

    mapa_departamentos = []

    for feature in geojson[
        "features"
    ]:

        propiedades = feature[
            "properties"
        ]

        original = propiedades.get(
            campo,
            ""
        )

        departamento = homologar(
            original
        )

        propiedades[
            "DEP_RADAR_15B"
        ] = departamento

        mapa_departamentos.append(
            departamento
        )

    mapa_departamentos = sorted(
        set(mapa_departamentos)
    )

    catalogo = pd.DataFrame(
        {
            "Departamento_Mapa":
                mapa_departamentos
        }
    )

    # --------------------------------------------------------
    # CRUCE DE MAPA + RADAR
    # --------------------------------------------------------

    base = catalogo.merge(
        df,
        on="Departamento_Mapa",
        how="left"
    )

    # Nombre visible
    base[
        "Departamento_Visible"
    ] = base[
        "Departamento"
    ]

    base.loc[
        base["Departamento_Visible"].isna(),
        "Departamento_Visible"
    ] = base[
        "Departamento_Mapa"
    ]

    # --------------------------------------------------------
    # ESTADO SEMÁFORO
    # --------------------------------------------------------

    base[
        "Estado_Semaforo"
    ] = base.apply(
        estado_semaforo,
        axis=1
    )

    base[
        "Recomendacion"
    ] = base.apply(
        recomendacion,
        axis=1
    )

    # --------------------------------------------------------
    # CAMPOS PARA HOVER SIN NAN
    # --------------------------------------------------------

    columnas_numericas = [
        "IRNA_Estructural",
        "IRNA_Ejecucion",
        "Brecha_IRNA",
        "PIM_Radar",
        "Registros_Radar",
        "Proyectos_Alta_Vocacion",
        "Proyectos_Con_Evidencia"
    ]

    for columna in columnas_numericas:

        if columna in base.columns:

            base[columna] = (
                base[columna]
                .fillna(0)
            )

    # ========================================================
    # MAPA
    # ========================================================

    orden_estados = [
        "FORTALEZA CONSOLIDADA",
        "BUENA EJECUCIÓN",
        "EN CONSOLIDACIÓN",
        "REQUIERE ACELERACIÓN",
        "BRECHA CRÍTICA",
        "SIN EVIDENCIA RADAR"
    ]

    colores = {
        "FORTALEZA CONSOLIDADA":
            "#217A5B",

        "BUENA EJECUCIÓN":
            "#5FAF83",

        "EN CONSOLIDACIÓN":
            "#E6C84F",

        "REQUIERE ACELERACIÓN":
            "#F39C45",

        "BRECHA CRÍTICA":
            "#D9534F",

        "SIN EVIDENCIA RADAR":
            "#C9CED3"
    }

    fig = px.choropleth(
        base,

        geojson=geojson,

        locations="Departamento_Mapa",

        featureidkey=(
            "properties.DEP_RADAR_15B"
        ),

        color="Estado_Semaforo",

        category_orders={
            "Estado_Semaforo":
                orden_estados
        },

        color_discrete_map=
            colores,

        hover_name=
            "Departamento_Visible",

        hover_data={

            "Departamento_Mapa":
                False,

            "Estado_Semaforo":
                True,

            "IRNA_Estructural":
                ":.1f",

            "IRNA_Ejecucion":
                ":.1f",

            "Brecha_IRNA":
                ":.1f",

            "PIM_Radar":
                ":,.0f",

            "Registros_Radar":
                True,

            "Proyectos_Alta_Vocacion":
                True,

            "Proyectos_Con_Evidencia":
                True,

            "Recomendacion":
                True
        },

        title=(
            "Semáforo Territorial IRNA — "
            "Turismo de Naturaleza y Aventura del Perú 2026"
        )
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(

        title={
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "size": 22
            }
        },

        legend_title_text=(
            "Estado territorial"
        ),

        legend={
            "orientation":
                "v",

            "x":
                0.78,

            "y":
                0.88
        },

        margin={
            "r": 40,
            "t": 80,
            "l": 30,
            "b": 30
        },

        paper_bgcolor=
            "white",

        geo_bgcolor=
            "white"
    )

    # ========================================================
    # EXPORTAR HTML
    # ========================================================

    fig.write_html(
        SALIDA,
        include_plotlyjs="cdn"
    )

    # ========================================================
    # RESUMEN
    # ========================================================

    resumen = (
        base.groupby(
            "Estado_Semaforo",
            as_index=False
        )
        .agg(
            Territorios=(
                "Departamento_Mapa",
                "count"
            ),

            PIM_Radar=(
                "PIM_Radar",
                "sum"
            )
        )
    )

    # ========================================================
    # EXPORTAR EXCEL
    # ========================================================

    with pd.ExcelWriter(
        SALIDA_DATOS,
        engine="openpyxl"
    ) as writer:

        base.to_excel(
            writer,
            sheet_name="Mapa_Semaforo",
            index=False
        )

        resumen.to_excel(
            writer,
            sheet_name="Resumen_Semaforo",
            index=False
        )

    # ========================================================
    # CONTROL
    # ========================================================

    print(
        "\n" + "=" * 100
    )

    print(
        "RESUMEN SEMÁFORO"
    )

    print(
        "=" * 100
    )

    print(
        resumen.to_string(
            index=False,
            formatters={
                "PIM_Radar":
                    lambda x:
                    f"{x:,.0f}"
            }
        )
    )

    sin_evidencia = base[
        base["Estado_Semaforo"]
        == "SIN EVIDENCIA RADAR"
    ][
        "Departamento_Mapa"
    ].tolist()

    print(
        "\nTERRITORIOS SIN EVIDENCIA RADAR:"
    )

    for departamento in sin_evidencia:

        print(
            f" - {departamento}"
        )

    print(
        "\n" + "=" * 100
    )

    print(
        "ARCHIVOS GENERADOS"
    )

    print(
        "=" * 100
    )

    print(
        f"1. {SALIDA}"
    )

    print(
        f"2. {SALIDA_DATOS}"
    )

    print(
        "\n✓ MAPA SEMÁFORO TERRITORIAL COMPLETADO"
    )

    print(
        "FIN"
    )


if __name__ == "__main__":
    main()