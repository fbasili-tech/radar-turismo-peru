from pathlib import Path
import json

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import folium
from folium.features import GeoJson, GeoJsonTooltip
from branca.colormap import linear
from streamlit_folium import st_folium

from modules.atdi import render_atdi
from modules.inversion import render_inversion
from modules.hubs_corredores import render_hubs_corredores
from modules.gestion_2030 import render_gestion_2030
from modules.datos_metodologia import render_datos_metodologia


# =============================================================================
# RADAR PERÚ APP V1
# VERSIÓN CONSOLIDADA
#
# MÓDULOS ACTIVOS
# -----------------------------------------------------------------------------
# 01 Radar Nacional
# 02 Mapa Territorial Interactivo
# 03 Inteligencia Territorial
# 04 ATTA / ATDI Alignment
# 05 Inversión Inteligente
#
# PRINCIPIOS
# -----------------------------------------------------------------------------
# - NO recalcula scores históricos
# - NO modifica IRNA-C
# - NO modifica outputs
# - Consume resultados validados
# - ATDI funciona como marco internacional de referencia
# =============================================================================


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

st.set_page_config(
    page_title="RADAR PERÚ",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# RUTAS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUTS = BASE_DIR / "outputs"

ARCHIVO_DASHBOARD = (
    OUTPUTS
    / "radar_dashboard_ejecutivo_v2_mef_2026.xlsx"
)

ARCHIVO_GEOJSON = (
    BASE_DIR
    / "app"
    / "data"
    / "peru_departamentos.geojson"
)


# =============================================================================
# ESTILO
# =============================================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    .radar-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #17365D;
        margin-bottom: 0;
    }

    .radar-subtitle {
        font-size: 1.05rem;
        color: #5C6770;
        margin-bottom: 1.2rem;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 750;
        color: #17365D;
        margin-top: 0.8rem;
        margin-bottom: 0.5rem;
    }

    .territory-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #17365D;
    }

    .decision-box {
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #D8DEE5;
        background: #F7F9FB;
        line-height: 1.65;
    }

    .territory-active {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        background: #EAF2F8;
        border-left: 5px solid #17365D;
        margin-top: 0.6rem;
        margin-bottom: 0.8rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# NORMALIZACIÓN TERRITORIAL
# =============================================================================

def normalizar(valor):

    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    equivalencias = {

        "ÁNCASH": "ANCASH",
        "ANCASH": "ANCASH",

        "APURÍMAC": "APURIMAC",
        "APURIMAC": "APURIMAC",

        "HUÁNUCO": "HUANUCO",
        "HUANUCO": "HUANUCO",

        "JUNÍN": "JUNIN",
        "JUNIN": "JUNIN",

        "SAN MARTÍN": "SAN MARTIN",
        "SAN MARTIN": "SAN MARTIN",

        "EL CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO",

        "CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO",

        "PROVINCIA CONSTITUCIONAL DEL CALLAO":
            "PROVINCIA CONSTITUCIONAL DEL CALLAO",

        "MUNICIPALIDAD METROPOLITANA DE LIMA":
            "__EXCLUIR__",
    }

    return equivalencias.get(
        texto,
        texto
    )


# =============================================================================
# UTILIDADES
# =============================================================================

def buscar_columna(
    df,
    candidatos
):

    if df is None or df.empty:
        return None

    mapa = {
        normalizar(c): c
        for c in df.columns
    }

    for candidato in candidatos:

        clave = normalizar(
            candidato
        )

        if clave in mapa:
            return mapa[clave]

    return None


def numero(
    fila,
    columna
):

    if columna is None:
        return np.nan

    try:

        return pd.to_numeric(
            pd.Series(
                [
                    fila.get(
                        columna,
                        np.nan
                    )
                ]
            ),
            errors="coerce"
        ).iloc[0]

    except Exception:

        return np.nan


def texto(
    fila,
    columna,
    default="N/D"
):

    if columna is None:
        return default

    valor = fila.get(
        columna,
        default
    )

    if pd.isna(valor):
        return default

    salida = str(
        valor
    ).strip()

    return salida if salida else default


def score(
    valor
):

    if pd.isna(valor):
        return "N/D"

    return f"{valor:.1f}"


# =============================================================================
# GEOMETRÍA
# =============================================================================

def punto_en_anillo(
    lon,
    lat,
    anillo
):

    dentro = False

    n = len(
        anillo
    )

    j = n - 1

    for i in range(n):

        xi = anillo[i][0]
        yi = anillo[i][1]

        xj = anillo[j][0]
        yj = anillo[j][1]

        cruza = (
            (yi > lat)
            !=
            (yj > lat)
        )

        if cruza:

            denominador = (
                yj - yi
            )

            if denominador == 0:
                denominador = 1e-12

            x_interseccion = (
                (xj - xi)
                *
                (lat - yi)
                /
                denominador
                +
                xi
            )

            if lon < x_interseccion:
                dentro = not dentro

        j = i

    return dentro


def punto_en_poligono(
    lon,
    lat,
    coordenadas
):

    if not coordenadas:
        return False

    exterior = coordenadas[
        0
    ]

    if not punto_en_anillo(
        lon,
        lat,
        exterior
    ):
        return False

    for hueco in coordenadas[
        1:
    ]:

        if punto_en_anillo(
            lon,
            lat,
            hueco
        ):
            return False

    return True


def punto_en_feature(
    lon,
    lat,
    feature
):

    geometria = feature.get(
        "geometry",
        {}
    )

    tipo = geometria.get(
        "type"
    )

    coordenadas = geometria.get(
        "coordinates",
        []
    )

    if tipo == "Polygon":

        return punto_en_poligono(
            lon,
            lat,
            coordenadas
        )

    if tipo == "MultiPolygon":

        for poligono in coordenadas:

            if punto_en_poligono(
                lon,
                lat,
                poligono
            ):
                return True

    return False


def territorio_desde_click(
    lat,
    lon,
    geojson
):

    for feature in geojson.get(
        "features",
        []
    ):

        if punto_en_feature(
            lon,
            lat,
            feature
        ):

            return feature.get(
                "properties",
                {}
            ).get(
                "RADAR_TERRITORIO"
            )

    return None


# =============================================================================
# CARGA DE DATOS
# =============================================================================

@st.cache_data
def leer_hoja(
    nombre
):

    return pd.read_excel(
        ARCHIVO_DASHBOARD,
        sheet_name=nombre
    )


@st.cache_data
def cargar_datos():

    if not ARCHIVO_DASHBOARD.exists():

        raise FileNotFoundError(
            f"No existe:\n{ARCHIVO_DASHBOARD}"
        )

    return {

        "ranking":
            leer_hoja(
                "02_Ranking_Territorial"
            ),

        "corredores":
            leer_hoja(
                "03_Hubs_Corredores"
            ),

        "kpi":
            leer_hoja(
                "06_KPI_Seguimiento"
            ),

        "mef":
            leer_hoja(
                "MEF_Territorial_V2"
            ),

        "oportunidades":
            leer_hoja(
                "MEF_Top_Oportunidades"
            ),

        "alertas":
            leer_hoja(
                "MEF_Alertas"
            ),
    }


# =============================================================================
# GEOJSON
# =============================================================================

@st.cache_data
def cargar_geojson():

    if not ARCHIVO_GEOJSON.exists():

        raise FileNotFoundError(
            f"No existe:\n{ARCHIVO_GEOJSON}"
        )

    with open(
        ARCHIVO_GEOJSON,
        "r",
        encoding="utf-8"
    ) as archivo:

        geo = json.load(
            archivo
        )

    nuevas_features = []

    for feature in geo.get(
        "features",
        []
    ):

        propiedades = feature.get(
            "properties",
            {}
        )

        nombre = normalizar(
            propiedades.get(
                "shapeName"
            )
        )

        if nombre == "__EXCLUIR__":
            continue

        propiedades[
            "RADAR_TERRITORIO"
        ] = nombre

        feature[
            "properties"
        ] = propiedades

        nuevas_features.append(
            feature
        )

    geo[
        "features"
    ] = nuevas_features

    return geo


# =============================================================================
# CARGA DEL SISTEMA
# =============================================================================

try:

    datos = cargar_datos()
    geojson = cargar_geojson()

except Exception as exc:

    st.error(
        "No fue posible cargar RADAR PERÚ."
    )

    st.exception(
        exc
    )

    st.stop()


ranking = datos[
    "ranking"
]

corredores = datos[
    "corredores"
]

kpi = datos[
    "kpi"
]

mef = datos[
    "mef"
]

oportunidades = datos[
    "oportunidades"
]

alertas = datos[
    "alertas"
]


# =============================================================================
# COLUMNAS
# =============================================================================

col_dep = buscar_columna(
    ranking,
    [
        "Departamento"
    ]
)

col_resources = buscar_columna(
    ranking,
    [
        "Perfil_Resources_Radar",
        "Perfil_Resources"
    ]
)

col_readiness = buscar_columna(
    ranking,
    [
        "Perfil_Readiness_Radar",
        "Perfil_Readiness"
    ]
)

col_comp = buscar_columna(
    ranking,
    [
        "Perfil_Competitividad_Radar"
    ]
)

col_rank = buscar_columna(
    ranking,
    [
        "Ranking_Perfil_Competitividad_Radar",
        "Ranking_Competitividad_Radar"
    ]
)

col_categoria = buscar_columna(
    ranking,
    [
        "Categoria_Final_Sistema",
        "Categoria_Sistema"
    ]
)

col_tipologia = buscar_columna(
    ranking,
    [
        "Tipologia_Competitividad_Radar"
    ]
)

col_dep_mef = buscar_columna(
    mef,
    [
        "Departamento",
        "Departamento_Radar"
    ]
)

col_dep_op = buscar_columna(
    oportunidades,
    [
        "Departamento"
    ]
)


# =============================================================================
# TERRITORIOS
# =============================================================================

departamentos = (
    ranking[
        col_dep
    ]
    .dropna()
    .astype(
        str
    )
    .str.strip()
    .sort_values()
    .unique()
    .tolist()
)


# =============================================================================
# ESTADO DE SESIÓN
# =============================================================================

if (
    "territorio_activo"
    not in st.session_state
):

    territorio_inicial = (
        "MADRE DE DIOS"
        if
        "MADRE DE DIOS"
        in departamentos
        else
        departamentos[0]
    )

    st.session_state[
        "territorio_activo"
    ] = territorio_inicial


if (
    "territorio_selector"
    not in st.session_state
):

    st.session_state[
        "territorio_selector"
    ] = st.session_state[
        "territorio_activo"
    ]


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:

    st.title(
        "🧭 RADAR PERÚ"
    )

    st.caption(
        "Nature & Adventure Tourism Intelligence"
    )

    st.divider()

    perfil_usuario = st.selectbox(
        "Perfil de uso",
        [
            "Gestión nacional",
            "Gestión territorial",
            "Inversión / cooperación",
            "Empresa / gremio",
            "Investigación / academia",
        ]
    )

    st.divider()

    st.markdown(
        "### Módulos"
    )

    st.write(
        "🏠 01 Radar Nacional"
    )

    st.write(
        "🗺️ 02 Mapa Territorial"
    )

    st.write(
        "📍 03 Inteligencia Territorial"
    )

    st.write(
        "🌎 04 ATTA / ATDI"
    )

    st.write(
        "💰 05 Inversión Inteligente"
    )

    st.write(
        "🔗 06 Hubs & Corredores"
    )

    st.write(
        "📈 07 Gestión 2030"
    )

    st.write(
        "📚 08 Datos & Metodología"
    )

    st.divider()

    st.caption(
        "PERU REFERENCE MODEL"
    )


# =============================================================================
# ENCABEZADO
# =============================================================================

st.markdown(
    '<div class="radar-title">RADAR PERÚ</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="radar-subtitle">

    Nature & Adventure Tourism Intelligence<br>

    Inteligencia territorial para la gestión del turismo
    de naturaleza y aventura

    </div>
    """,
    unsafe_allow_html=True
)


# =============================================================================
# 01 RADAR NACIONAL
# =============================================================================

st.markdown(
    '<div class="section-title">01 · Radar Nacional</div>',
    unsafe_allow_html=True
)


territorios = ranking[
    col_dep
].nunique()


n_corredores = len(
    corredores
)


col_id_kpi = buscar_columna(
    kpi,
    [
        "ID_KPI"
    ]
)


n_kpi = (
    kpi[
        col_id_kpi
    ].nunique()
    if col_id_kpi
    else len(
        kpi
    )
)


pim_total = pd.to_numeric(
    mef[
        "PIM_MEF"
    ],
    errors="coerce"
).sum()


dev_total = pd.to_numeric(
    mef[
        "Devengado_MEF"
    ],
    errors="coerce"
).sum()


avance_nacional = (
    dev_total
    /
    pim_total
    *
    100
    if pim_total > 0
    else 0
)


c1, c2, c3, c4, c5 = st.columns(
    5
)


c1.metric(
    "Territorios",
    territorios
)

c2.metric(
    "Corredores",
    n_corredores
)

c3.metric(
    "KPI",
    n_kpi
)

c4.metric(
    "PIM 2026",
    f"S/ {pim_total / 1_000_000:.1f} M"
)

c5.metric(
    "Ejecución",
    f"{avance_nacional:.1f}%"
)


st.divider()


# =============================================================================
# BASE TERRITORIAL INTEGRADA
# =============================================================================

mapa_df = ranking.copy()


mapa_df[
    "RADAR_TERRITORIO"
] = mapa_df[
    col_dep
].apply(
    normalizar
)


mef_aux = mef.copy()


mef_aux[
    "RADAR_TERRITORIO"
] = mef_aux[
    col_dep_mef
].apply(
    normalizar
)


columnas_mef = [
    "RADAR_TERRITORIO",
    "PIM_MEF",
    "Devengado_MEF",
    "Avance_MEF_Pct",
    "Score_Oportunidad_Inversion_MEF",
    "Prioridad_Cartera",
    "Categoria_Alineamiento_MEF",
    "Decision_Estrategica_MEF",
]


columnas_mef = [
    c
    for c in columnas_mef
    if c in mef_aux.columns
]


mapa_df = mapa_df.merge(
    mef_aux[
        columnas_mef
    ],
    on="RADAR_TERRITORIO",
    how="left"
)


# =============================================================================
# 02 MAPA TERRITORIAL
# =============================================================================

st.markdown(
    '<div class="section-title">02 · Mapa Territorial Interactivo</div>',
    unsafe_allow_html=True
)


st.caption(
    "Seleccione un indicador o haga clic directamente "
    "sobre un departamento."
)


opciones_mapa = {}


if col_comp:

    opciones_mapa[
        "Competitividad Radar"
    ] = col_comp


if col_resources:

    opciones_mapa[
        "Resources"
    ] = col_resources


if col_readiness:

    opciones_mapa[
        "Readiness"
    ] = col_readiness


if "PIM_MEF" in mapa_df.columns:

    opciones_mapa[
        "PIM MEF"
    ] = "PIM_MEF"


if "Avance_MEF_Pct" in mapa_df.columns:

    opciones_mapa[
        "Ejecución MEF"
    ] = "Avance_MEF_Pct"


if (
    "Score_Oportunidad_Inversion_MEF"
    in mapa_df.columns
):

    opciones_mapa[
        "Oportunidad de inversión"
    ] = "Score_Oportunidad_Inversion_MEF"


indicador_mapa = st.selectbox(
    "Indicador del mapa",
    list(
        opciones_mapa.keys()
    ),
    key="indicador_mapa"
)


columna_mapa = opciones_mapa[
    indicador_mapa
]


mapa_df[
    columna_mapa
] = pd.to_numeric(
    mapa_df[
        columna_mapa
    ],
    errors="coerce"
)


# =============================================================================
# ESCALA CARTOGRÁFICA
# =============================================================================

valores = (
    mapa_df
    .set_index(
        "RADAR_TERRITORIO"
    )[
        columna_mapa
    ]
    .to_dict()
)


serie_valores = pd.to_numeric(
    mapa_df[
        columna_mapa
    ],
    errors="coerce"
).dropna()


if serie_valores.empty:

    minimo = 0
    maximo = 100

else:

    minimo = float(
        serie_valores.min()
    )

    maximo = float(
        serie_valores.max()
    )


if minimo == maximo:

    maximo = minimo + 1


colormap = linear.YlGnBu_09.scale(
    minimo,
    maximo
)


colormap.caption = indicador_mapa


# =============================================================================
# GEOJSON + DATOS
# =============================================================================

mapa_lookup = (
    mapa_df
    .set_index(
        "RADAR_TERRITORIO"
    )
    .to_dict(
        orient="index"
    )
)


geo_mapa = json.loads(
    json.dumps(
        geojson
    )
)


for feature in geo_mapa[
    "features"
]:

    props = feature[
        "properties"
    ]

    territorio_geo = props[
        "RADAR_TERRITORIO"
    ]

    registro = mapa_lookup.get(
        territorio_geo,
        {}
    )

    props[
        "INDICADOR"
    ] = registro.get(
        columna_mapa
    )

    props[
        "COMPETITIVIDAD"
    ] = registro.get(
        col_comp
    )

    props[
        "RESOURCES"
    ] = registro.get(
        col_resources
    )

    props[
        "READINESS"
    ] = registro.get(
        col_readiness
    )

    props[
        "PIM_MEF"
    ] = registro.get(
        "PIM_MEF"
    )

    props[
        "AVANCE_MEF"
    ] = registro.get(
        "Avance_MEF_Pct"
    )

    props[
        "OPORTUNIDAD_MEF"
    ] = registro.get(
        "Score_Oportunidad_Inversion_MEF"
    )


# =============================================================================
# MAPA FOLIUM
# =============================================================================

mapa = folium.Map(
    location=[
        -9.2,
        -75.0
    ],
    zoom_start=5,
    tiles="CartoDB positron",
    control_scale=True
)


def estilo(
    feature
):

    territorio_feature = feature[
        "properties"
    ][
        "RADAR_TERRITORIO"
    ]

    valor = valores.get(
        territorio_feature,
        np.nan
    )

    if pd.isna(
        valor
    ):

        color = "#D9D9D9"

    else:

        color = colormap(
            float(
                valor
            )
        )

    es_activo = (
        territorio_feature
        ==
        normalizar(
            st.session_state[
                "territorio_activo"
            ]
        )
    )

    return {

        "fillColor":
            color,

        "color":
            (
                "#C00000"
                if es_activo
                else "#555555"
            ),

        "weight":
            (
                4
                if es_activo
                else 1
            ),

        "fillOpacity":
            (
                0.9
                if es_activo
                else 0.75
            ),
    }


tooltip = GeoJsonTooltip(

    fields=[
        "RADAR_TERRITORIO",
        "COMPETITIVIDAD",
        "RESOURCES",
        "READINESS",
        "PIM_MEF",
        "AVANCE_MEF",
        "OPORTUNIDAD_MEF",
    ],

    aliases=[
        "Territorio:",
        "Competitividad:",
        "Resources:",
        "Readiness:",
        "PIM MEF:",
        "Ejecución MEF:",
        "Oportunidad inversión:",
    ],

    localize=True,
    sticky=False,
    labels=True,
)


GeoJson(
    geo_mapa,
    name="RADAR PERÚ",
    style_function=estilo,
    tooltip=tooltip,
    highlight_function=lambda x: {
        "weight": 3,
        "color": "#17365D",
        "fillOpacity": 0.9,
    }
).add_to(
    mapa
)


colormap.add_to(
    mapa
)


resultado_mapa = st_folium(
    mapa,
    width=None,
    height=650,
    use_container_width=True,
    returned_objects=[
        "last_object_clicked"
    ],
    key="mapa_radar_peru"
)


# =============================================================================
# CLIC EN MAPA
# =============================================================================

click = resultado_mapa.get(
    "last_object_clicked"
)


if click:

    lat_click = click.get(
        "lat"
    )

    lon_click = click.get(
        "lng"
    )

    if (
        lat_click is not None
        and
        lon_click is not None
    ):

        territorio_click = territorio_desde_click(
            lat_click,
            lon_click,
            geojson
        )

        if (
            territorio_click
            and
            territorio_click
            !=
            normalizar(
                st.session_state[
                    "territorio_activo"
                ]
            )
        ):

            coincidencia = ranking[
                ranking[
                    col_dep
                ]
                .astype(
                    str
                )
                .map(
                    normalizar
                )
                ==
                territorio_click
            ]

            if not coincidencia.empty:

                nombre_visible = str(
                    coincidencia[
                        col_dep
                    ].iloc[
                        0
                    ]
                )

                st.session_state[
                    "territorio_activo"
                ] = nombre_visible

                st.session_state[
                    "territorio_selector"
                ] = nombre_visible

                st.rerun()


st.caption(
    "Fuente cartográfica: geoBoundaries ADM1 · "
    "Normalización territorial validada 25/25."
)


st.markdown(
    f"""
    <div class="territory-active">

    <b>Territorio activo:</b>
    {st.session_state["territorio_activo"]}

    </div>
    """,
    unsafe_allow_html=True
)


# =============================================================================
# RANKING NACIONAL
# =============================================================================

st.divider()


izquierda, derecha = st.columns(
    [
        1.15,
        0.85
    ]
)


with izquierda:

    st.markdown(
        "#### Competitividad territorial"
    )

    top_comp = ranking[
        [
            col_dep,
            col_comp
        ]
    ].copy()

    top_comp[
        col_comp
    ] = pd.to_numeric(
        top_comp[
            col_comp
        ],
        errors="coerce"
    )

    top_comp = (
        top_comp
        .dropna(
            subset=[
                col_comp
            ]
        )
        .sort_values(
            col_comp,
            ascending=False
        )
        .head(
            10
        )
    )

    fig_comp = px.bar(
        top_comp.sort_values(
            col_comp
        ),
        x=col_comp,
        y=col_dep,
        orientation="h",
        text=col_comp,
        labels={
            col_comp:
                "Competitividad Radar",

            col_dep:
                "Territorio"
        }
    )

    fig_comp.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_comp.update_layout(
        height=420,
        yaxis_title=None,
        xaxis_title="Competitividad Radar",
        margin=dict(
            l=0,
            r=20,
            t=10,
            b=10
        )
    )

    st.plotly_chart(
        fig_comp,
        width="stretch"
    )


with derecha:

    st.markdown(
        "#### Oportunidades de inversión"
    )

    columnas_op = [
        c
        for c in [
            "Ranking_Oportunidad_MEF",
            "Departamento",
            "PIM_MEF",
            "Avance_MEF_Pct",
            "Score_Oportunidad_Inversion_MEF"
        ]
        if c in oportunidades.columns
    ]

    tabla_op = oportunidades[
        columnas_op
    ].copy()

    if (
        "Ranking_Oportunidad_MEF"
        in tabla_op.columns
    ):

        tabla_op = tabla_op.sort_values(
            "Ranking_Oportunidad_MEF"
        )

    tabla_op = tabla_op.head(
        10
    )

    st.dataframe(
        tabla_op,
        hide_index=True,
        width="stretch"
    )


# =============================================================================
# 03 INTELIGENCIA TERRITORIAL
# =============================================================================

st.divider()


st.markdown(
    '<div class="section-title">03 · Inteligencia Territorial</div>',
    unsafe_allow_html=True
)


territorio_selector = st.selectbox(
    "Seleccione territorio",
    departamentos,
    key="territorio_selector"
)


if (
    territorio_selector
    !=
    st.session_state[
        "territorio_activo"
    ]
):

    st.session_state[
        "territorio_activo"
    ] = territorio_selector

    st.rerun()


departamento_seleccionado = st.session_state[
    "territorio_activo"
]


fila = ranking[
    ranking[
        col_dep
    ]
    .astype(
        str
    )
    .map(
        normalizar
    )
    ==
    normalizar(
        departamento_seleccionado
    )
]


if fila.empty:

    st.stop()


territorio = fila.iloc[
    0
]


resources = numero(
    territorio,
    col_resources
)

readiness = numero(
    territorio,
    col_readiness
)

competitividad = numero(
    territorio,
    col_comp
)

ranking_nacional = numero(
    territorio,
    col_rank
)

categoria = texto(
    territorio,
    col_categoria
)

tipologia = texto(
    territorio,
    col_tipologia
)


# =============================================================================
# CABECERA TERRITORIAL
# =============================================================================

st.markdown(
    f"""
    <div class="territory-title">
    {departamento_seleccionado}
    </div>
    """,
    unsafe_allow_html=True
)


t1, t2, t3 = st.columns(
    3
)


t1.metric(
    "Resources",
    score(
        resources
    )
)

t2.metric(
    "Readiness",
    score(
        readiness
    )
)

t3.metric(
    "Competitividad Radar",
    score(
        competitividad
    )
)


r1, r2 = st.columns(
    2
)


r1.metric(
    "Ranking nacional",
    (
        f"#{int(ranking_nacional)}"
        if pd.notna(
            ranking_nacional
        )
        else "N/D"
    )
)


r2.metric(
    "Rol territorial",
    categoria
)


if tipologia != "N/D":

    st.info(
        f"Tipología: {tipologia}"
    )


# =============================================================================
# RADAR CHART
# =============================================================================

prom_resources = pd.to_numeric(
    ranking[
        col_resources
    ],
    errors="coerce"
).mean()


prom_readiness = pd.to_numeric(
    ranking[
        col_readiness
    ],
    errors="coerce"
).mean()


prom_comp = pd.to_numeric(
    ranking[
        col_comp
    ],
    errors="coerce"
).mean()


categorias = [
    "Resources",
    "Readiness",
    "Competitividad"
]


territorio_valores = [
    resources,
    readiness,
    competitividad
]


promedio_valores = [
    prom_resources,
    prom_readiness,
    prom_comp
]


categorias_plot = categorias + [
    categorias[0]
]


territorio_plot = territorio_valores + [
    territorio_valores[0]
]


promedio_plot = promedio_valores + [
    promedio_valores[0]
]


fig_radar = go.Figure()


fig_radar.add_trace(
    go.Scatterpolar(
        r=territorio_plot,
        theta=categorias_plot,
        fill="toself",
        name=departamento_seleccionado
    )
)


fig_radar.add_trace(
    go.Scatterpolar(
        r=promedio_plot,
        theta=categorias_plot,
        fill="toself",
        name="Promedio nacional",
        opacity=0.45
    )
)


fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[
                0,
                100
            ]
        )
    ),
    height=430
)


st.plotly_chart(
    fig_radar,
    width="stretch"
)


# =============================================================================
# COMPARACIÓN
# =============================================================================

comparacion = pd.DataFrame(
    {
        "Dimensión":
            categorias,

        departamento_seleccionado:
            territorio_valores,

        "Promedio nacional":
            promedio_valores
    }
)


comparacion[
    "Brecha vs promedio"
] = (
    comparacion[
        departamento_seleccionado
    ]
    -
    comparacion[
        "Promedio nacional"
    ]
)


for c in [
    departamento_seleccionado,
    "Promedio nacional",
    "Brecha vs promedio"
]:

    comparacion[
        c
    ] = pd.to_numeric(
        comparacion[
            c
        ],
        errors="coerce"
    ).round(
        1
    )


st.dataframe(
    comparacion,
    hide_index=True,
    width="stretch"
)


# =============================================================================
# MEF TERRITORIAL
# =============================================================================

fila_mef = mef[
    mef[
        col_dep_mef
    ]
    .astype(
        str
    )
    .map(
        normalizar
    )
    ==
    normalizar(
        departamento_seleccionado
    )
]


if not fila_mef.empty:

    mef_t = fila_mef.iloc[
        0
    ]


    pim = numero(
        mef_t,
        buscar_columna(
            mef,
            [
                "PIM_MEF"
            ]
        )
    )


    dev = numero(
        mef_t,
        buscar_columna(
            mef,
            [
                "Devengado_MEF"
            ]
        )
    )


    avance = numero(
        mef_t,
        buscar_columna(
            mef,
            [
                "Avance_MEF_Pct"
            ]
        )
    )


    oportunidad = numero(
        mef_t,
        buscar_columna(
            mef,
            [
                "Score_Oportunidad_Inversion_MEF"
            ]
        )
    )


    i1, i2, i3, i4 = st.columns(
        4
    )


    i1.metric(
        "PIM",
        (
            f"S/ {pim / 1_000_000:.2f} M"
            if pd.notna(
                pim
            )
            else "N/D"
        )
    )


    i2.metric(
        "Devengado",
        (
            f"S/ {dev / 1_000_000:.2f} M"
            if pd.notna(
                dev
            )
            else "N/D"
        )
    )


    i3.metric(
        "Ejecución",
        (
            f"{avance:.1f}%"
            if pd.notna(
                avance
            )
            else "N/D"
        )
    )


    i4.metric(
        "Score oportunidad",
        score(
            oportunidad
        )
    )


# =============================================================================
# DECISIÓN TERRITORIAL
# =============================================================================

fila_op = oportunidades[
    oportunidades[
        col_dep_op
    ]
    .astype(
        str
    )
    .map(
        normalizar
    )
    ==
    normalizar(
        departamento_seleccionado
    )
]


decision = (
    "MONITOREAR Y PROFUNDIZAR DIAGNÓSTICO"
)

categoria_mef = "N/D"
prioridad = "N/D"
score_mef = np.nan


if not fila_op.empty:

    op = fila_op.iloc[
        0
    ]


    decision = texto(
        op,
        buscar_columna(
            oportunidades,
            [
                "Decision_Estrategica_MEF"
            ]
        ),
        decision
    )


    categoria_mef = texto(
        op,
        buscar_columna(
            oportunidades,
            [
                "Categoria_Alineamiento_MEF"
            ]
        )
    )


    prioridad = texto(
        op,
        buscar_columna(
            oportunidades,
            [
                "Prioridad_Cartera"
            ]
        )
    )


    score_mef = numero(
        op,
        buscar_columna(
            oportunidades,
            [
                "Score_Oportunidad_Inversion_MEF"
            ]
        )
    )


# =============================================================================
# INTERPRETACIÓN
# =============================================================================

mensajes = []


if (
    pd.notna(
        resources
    )
    and
    pd.notna(
        readiness
    )
):

    brecha = (
        resources
        -
        readiness
    )


    if brecha >= 15:

        mensajes.append(
            "Existe una brecha relevante entre "
            "la base de recursos y el nivel de preparación."
        )

    elif brecha <= -10:

        mensajes.append(
            "La preparación territorial supera "
            "relativamente la fortaleza de recursos."
        )

    else:

        mensajes.append(
            "Resources y Readiness presentan "
            "una relación relativamente equilibrada."
        )


if pd.notna(
    competitividad
):

    if competitividad >= 60:

        mensajes.append(
            "El territorio se encuentra entre los perfiles "
            "más competitivos del sistema Radar."
        )

    elif competitividad >= 40:

        mensajes.append(
            "Presenta competitividad intermedia "
            "y oportunidades de fortalecimiento."
        )

    else:

        mensajes.append(
            "Persisten brechas importantes "
            "de competitividad territorial."
        )


if not mensajes:

    mensajes.append(
        "La interpretación requiere información "
        "territorial complementaria."
    )


diagnostico = " ".join(
    mensajes
)


st.markdown(
    "#### ¿Qué me dice el Radar?"
)


st.markdown(
    f"""
    <div class="decision-box">

    <b>{departamento_seleccionado}</b>

    <br><br>

    {diagnostico}

    <br><br>

    <b>Rol territorial:</b>
    {categoria}

    <br>

    <b>Prioridad:</b>
    {prioridad}

    <br>

    <b>Alineamiento inversión / prioridad:</b>
    {categoria_mef}

    <br>

    <b>Score oportunidad:</b>
    {score(score_mef)}

    <br><br>

    <b>DECISIÓN ESTRATÉGICA</b><br>
    {decision}

    </div>
    """,
    unsafe_allow_html=True
)


# =============================================================================
# 04 ATTA / ATDI ALIGNMENT
# =============================================================================

render_atdi(
    departamento_seleccionado
)


# =============================================================================
# 05 INVERSIÓN INTELIGENTE
# =============================================================================

render_inversion(
    departamento_seleccionado
)

# =============================================================================
# 06 HUBS & CORREDORES
# =============================================================================

render_hubs_corredores(
    departamento_seleccionado
)

# =============================================================================
# 07 GESTION 2030
# =============================================================================

render_gestion_2030(
    departamento_seleccionado
)

# =============================================================================
# 08 DATOS & METODOLOGIA
# =============================================================================

render_datos_metodologia()
