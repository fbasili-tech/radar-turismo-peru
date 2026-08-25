from pathlib import Path
import json
import unicodedata
import re

import pandas as pd
import requests
import plotly.express as px


# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 15: MAPA TERRITORIAL INTERACTIVO
# ============================================================

ENTRADA = Path(
    "outputs/radar_turismo_irna_calibrado_2026.xlsx"
)

CARPETA_SALIDA = Path("outputs")

GEOJSON_LOCAL = Path(
    "data/peru_departamentos.geojson"
)

SALIDA_IRNA = Path(
    "outputs/mapa_irna_estructural_peru_2026.html"
)

SALIDA_BRECHA = Path(
    "outputs/mapa_brechas_irna_peru_2026.html"
)

SALIDA_DATOS = Path(
    "outputs/radar_mapa_territorial_2026.xlsx"
)


# ============================================================
# FUENTES GEOJSON
# ============================================================

# Intentaremos varias fuentes públicas.
# Si una falla, el script prueba la siguiente.

FUENTES_GEOJSON = [
    "https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_departamental_simple.geojson",
    "https://raw.githubusercontent.com/angelnmara/geojson/master/peru/peru_departamental_simple.geojson",
]


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


# ============================================================
# HOMOLOGACIÓN DE DEPARTAMENTOS
# ============================================================

EQUIVALENCIAS = {

    "PROVINCIA CONSTITUCIONAL DEL CALLAO":
        "CALLAO",

    "CALLAO":
        "CALLAO",

    "ANCASH":
        "ANCASH",

    "SAN MARTIN":
        "SAN MARTIN",

    "HUANUCO":
        "HUANUCO"
}


def homologar_departamento(nombre):

    nombre = normalizar(nombre)

    return EQUIVALENCIAS.get(
        nombre,
        nombre
    )


# ============================================================
# DESCARGAR GEOJSON
# ============================================================

def descargar_geojson():

    GEOJSON_LOCAL.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if GEOJSON_LOCAL.exists():

        print(
            "\nGeoJSON local encontrado:"
        )

        print(
            GEOJSON_LOCAL
        )

        return True

    print(
        "\nDescargando mapa departamental del Perú..."
    )

    for url in FUENTES_GEOJSON:

        try:

            print(
                f"Probando fuente:\n{url}"
            )

            respuesta = requests.get(
                url,
                timeout=30
            )

            if respuesta.status_code == 200:

                contenido = respuesta.json()

                with open(
                    GEOJSON_LOCAL,
                    "w",
                    encoding="utf-8"
                ) as archivo:

                    json.dump(
                        contenido,
                        archivo,
                        ensure_ascii=False
                    )

                print(
                    "\n✓ GEOJSON DESCARGADO"
                )

                return True

        except Exception as error:

            print(
                f"No se pudo usar esta fuente: {error}"
            )

    return False


# ============================================================
# DETECTAR CAMPO DEL NOMBRE DE DEPARTAMENTO
# ============================================================

def detectar_campo_departamento(geojson):

    if not geojson.get("features"):

        raise ValueError(
            "El GeoJSON no contiene features."
        )

    propiedades = (
        geojson["features"][0]
        .get(
            "properties",
            {}
        )
    )

    candidatos = [
        "NOMBDEP",
        "NOMB_DEPA",
        "DEPARTAMEN",
        "DEPARTAMENTO",
        "departamento",
        "name",
        "NAME_1",
        "NOMBRE"
    ]

    for campo in candidatos:

        if campo in propiedades:

            return campo

    print(
        "\nCampos encontrados en GeoJSON:"
    )

    print(
        list(propiedades.keys())
    )

    raise ValueError(
        "No fue posible identificar automáticamente "
        "el campo del nombre del departamento."
    )


# ============================================================
# PREPARAR GEOJSON
# ============================================================

def preparar_geojson():

    if not descargar_geojson():

        raise RuntimeError(
            "\nNo fue posible descargar el mapa.\n"
            "Verifica que la computadora tenga conexión "
            "a Internet e intenta nuevamente."
        )

    with open(
        GEOJSON_LOCAL,
        "r",
        encoding="utf-8"
    ) as archivo:

        geojson = json.load(
            archivo
        )

    campo = detectar_campo_departamento(
        geojson
    )

    print(
        f"\nCampo territorial detectado: {campo}"
    )

    # Crear un identificador estandarizado
    for feature in geojson[
        "features"
    ]:

        original = (
            feature
            .get(
                "properties",
                {}
            )
            .get(
                campo,
                ""
            )
        )

        feature[
            "properties"
        ][
            "DEP_RADAR"
        ] = homologar_departamento(
            original
        )

    return geojson


# ============================================================
# CATEGORÍA EJECUTIVA
# ============================================================

def clasificacion_ejecutiva(row):

    estructural = row[
        "IRNA_Estructural"
    ]

    ejecucion = row[
        "IRNA_Ejecucion"
    ]

    if (
        estructural >= 60
        and ejecucion >= 60
    ):
        return "FORTALEZA CONSOLIDADA"

    if (
        estructural >= 60
        and ejecucion < 40
    ):
        return "ALTO POTENCIAL / EJECUCIÓN CRÍTICA"

    if estructural >= 60:

        return "ALTO POTENCIAL"

    if (
        estructural >= 45
        and ejecucion >= 60
    ):

        return "EMERGENTE / BUENA EJECUCIÓN"

    if estructural >= 45:

        return "EN CONSOLIDACIÓN"

    return "EMERGENTE"


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():

    print("=" * 100)
    print(
        "RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ"
    )
    print(
        "15 - MAPA TERRITORIAL INTERACTIVO"
    )
    print("=" * 100)

    CARPETA_SALIDA.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # CARGAR IRNA V2
    # --------------------------------------------------------

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Sintesis_IRNA_V2"
    )

    print(
        f"\nTerritorios cargados: {len(df)}"
    )

    df[
        "Departamento_Mapa"
    ] = (
        df[
            "Departamento"
        ]
        .apply(
            homologar_departamento
        )
    )

    df[
        "Clasificacion_Ejecutiva"
    ] = df.apply(
        clasificacion_ejecutiva,
        axis=1
    )

    # --------------------------------------------------------
    # PREPARAR MAPA
    # --------------------------------------------------------

    geojson = preparar_geojson()

    departamentos_mapa = set()

    for feature in geojson[
        "features"
    ]:

        departamentos_mapa.add(
            feature[
                "properties"
            ][
                "DEP_RADAR"
            ]
        )

    departamentos_radar = set(
        df[
            "Departamento_Mapa"
        ]
    )

    encontrados = (
        departamentos_radar
        & departamentos_mapa
    )

    no_encontrados = (
        departamentos_radar
        - departamentos_mapa
    )

    print(
        "\n" + "=" * 100
    )

    print(
        "CONTROL DE HOMOLOGACIÓN TERRITORIAL"
    )

    print(
        "=" * 100
    )

    print(
        f"Territorios Radar     : "
        f"{len(departamentos_radar)}"
    )

    print(
        f"Territorios encontrados: "
        f"{len(encontrados)}"
    )

    if no_encontrados:

        print(
            "\n⚠ TERRITORIOS NO ENCONTRADOS:"
        )

        for departamento in sorted(
            no_encontrados
        ):

            print(
                f" - {departamento}"
            )

    else:

        print(
            "\n✓ TODOS LOS TERRITORIOS "
            "FUERON HOMOLOGADOS"
        )

    # ========================================================
    # MAPA 1 — IRNA ESTRUCTURAL
    # ========================================================

    fig_irna = px.choropleth(
        df,
        geojson=geojson,
        locations="Departamento_Mapa",
        featureidkey="properties.DEP_RADAR",
        color="IRNA_Estructural",

        hover_name="Departamento",

        hover_data={
            "Departamento_Mapa": False,
            "IRNA_Estructural": ":.1f",
            "IRNA_Ejecucion": ":.1f",
            "Brecha_IRNA": ":.1f",
            "PIM_Radar": ":,.0f",
            "Registros_Radar": True,
            "Proyectos_Alta_Vocacion": True,
            "Clasificacion_Ejecutiva": True
        },

        color_continuous_scale=[
            "#E8F3EE",
            "#B7D8CA",
            "#72B39A",
            "#2E7D5B",
            "#143D33"
        ],

        title=(
            "IRNA Estructural — Turismo de Naturaleza "
            "y Aventura del Perú 2026"
        )
    )

    fig_irna.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig_irna.update_layout(

        title={
            "x": 0.5,
            "xanchor": "center"
        },

        margin={
            "r": 20,
            "t": 70,
            "l": 20,
            "b": 20
        },

        coloraxis_colorbar={
            "title": "IRNA"
        }
    )

    fig_irna.write_html(
        SALIDA_IRNA,
        include_plotlyjs="cdn"
    )

    # ========================================================
    # MAPA 2 — BRECHAS
    # ========================================================

    fig_brecha = px.choropleth(
        df,
        geojson=geojson,
        locations="Departamento_Mapa",
        featureidkey="properties.DEP_RADAR",
        color="Brecha_IRNA",

        hover_name="Departamento",

        hover_data={
            "Departamento_Mapa": False,
            "IRNA_Estructural": ":.1f",
            "IRNA_Ejecucion": ":.1f",
            "Brecha_IRNA": ":.1f",
            "Categoria_Brecha": True,
            "PIM_Radar": ":,.0f"
        },

        color_continuous_scale=[
            "#2E7D5B",
            "#F4D35E",
            "#F0A04B",
            "#D9534F"
        ],

        title=(
            "Brecha IRNA — Potencial estructural "
            "vs ejecución 2026"
        )
    )

    fig_brecha.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig_brecha.update_layout(

        title={
            "x": 0.5,
            "xanchor": "center"
        },

        margin={
            "r": 20,
            "t": 70,
            "l": 20,
            "b": 20
        },

        coloraxis_colorbar={
            "title": "Brecha"
        }
    )

    fig_brecha.write_html(
        SALIDA_BRECHA,
        include_plotlyjs="cdn"
    )

    # ========================================================
    # EXPORTAR DATOS DEL MAPA
    # ========================================================

    columnas = [
        "Departamento",
        "Departamento_Mapa",
        "IRNA_Estructural",
        "Categoria_Estructural",
        "IRNA_Ejecucion",
        "Categoria_Ejecucion",
        "Brecha_IRNA",
        "Categoria_Brecha",
        "Clasificacion_Ejecutiva",
        "PIM_Radar",
        "Registros_Radar",
        "Proyectos_Alta_Vocacion",
        "Proyectos_Con_Evidencia",
        "Diversidad_Ambitos",
        "Diversidad_Intervenciones"
    ]

    df[
        columnas
    ].to_excel(
        SALIDA_DATOS,
        index=False
    )

    # ========================================================
    # RANKING
    # ========================================================

    ranking = (
        df[
            [
                "Departamento",
                "IRNA_Estructural",
                "IRNA_Ejecucion",
                "Brecha_IRNA",
                "Clasificacion_Ejecutiva"
            ]
        ]
        .sort_values(
            "IRNA_Estructural",
            ascending=False
        )
    )

    print(
        "\n" + "=" * 100
    )

    print(
        "TOP 10 TERRITORIAL"
    )

    print(
        "=" * 100
    )

    print(
        ranking
        .head(10)
        .to_string(
            index=False
        )
    )

    # ========================================================
    # SALIDAS
    # ========================================================

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
        f"\n1. {SALIDA_IRNA}"
    )

    print(
        f"2. {SALIDA_BRECHA}"
    )

    print(
        f"3. {SALIDA_DATOS}"
    )

    print(
        "\n✓ MAPA TERRITORIAL DEL RADAR COMPLETADO"
    )

    print(
        "FIN"
    )


if __name__ == "__main__":
    main()