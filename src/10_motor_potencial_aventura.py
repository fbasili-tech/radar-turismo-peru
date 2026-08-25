from pathlib import Path
import pandas as pd
import unicodedata
import re

# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 10: MOTOR DE POTENCIAL DE AVENTURA
# ============================================================

ENTRADA = Path(
    "outputs/radar_turismo_matriz_impacto_2026.xlsx"
)

SALIDA = Path(
    "outputs/radar_turismo_potencial_aventura_2026.xlsx"
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
# ACTIVIDADES EXPLÍCITAS
# ============================================================

ACTIVIDADES_EXPLICITAS = {

    "TREKKING_SENDERISMO": [
        "trekking",
        "senderismo",
        "caminata"
    ],

    "MONTANISMO": [
        "montanismo",
        "andinismo"
    ],

    "ESCALADA": [
        "escalada",
        "rapel",
        "rappel",
        "via ferrata"
    ],

    "RAFTING_CANOTAJE": [
        "rafting",
        "canotaje"
    ],

    "KAYAK": [
        "kayak",
        "kayaking"
    ],

    "SURF": [
        "surf"
    ],

    "BUCEO_SNORKEL": [
        "buceo",
        "snorkel"
    ],

    "CICLISMO": [
        "ciclismo",
        "bicicleta",
        "mountain bike"
    ],

    "PARAPENTE": [
        "parapente"
    ],

    "TIROLESA": [
        "tirolesa",
        "zipline"
    ],

    "CABALGATA": [
        "cabalgata"
    ],

    "CAMPAMENTO": [
        "campamento",
        "camping"
    ],

    "SANDBOARD": [
        "sandboard"
    ]
}


# ============================================================
# REGLAS DE INFERENCIA
# ============================================================

INDICADORES = {

    "AGUA_FLUVIAL": [
        "rio",
        "rios",
        "catarata",
        "cataratas",
        "quebrada",
        "cañon",
        "canon"
    ],

    "AGUA_LACUSTRE": [
        "lago",
        "lagos",
        "laguna",
        "lagunas"
    ],

    "MAR_COSTA": [
        "mar",
        "marino",
        "playa",
        "playas",
        "bahia",
        "litoral",
        "costa"
    ],

    "MONTANA": [
        "montana",
        "montanas",
        "cordillera",
        "nevado",
        "nevados",
        "glaciar",
        "glaciares"
    ],

    "SENDEROS": [
        "sendero",
        "senderos",
        "ruta",
        "rutas",
        "camino",
        "caminos",
        "circuito",
        "circuitos"
    ],

    "NATURALEZA": [
        "bosque",
        "bosques",
        "selva",
        "flora",
        "fauna",
        "biodiversidad",
        "area natural",
        "parque nacional",
        "reserva nacional"
    ],

    "OBSERVACION": [
        "observacion",
        "avistamiento",
        "mirador",
        "miradores"
    ],

    "ACCESO": [
        "acceso",
        "accesibilidad",
        "carretera",
        "via",
        "vias",
        "puente"
    ]
}


# ============================================================
# DETECCIÓN DE ACTIVIDAD EXPLÍCITA
# ============================================================

def detectar_actividades_explicitas(texto):

    actividades = []

    for actividad, palabras in ACTIVIDADES_EXPLICITAS.items():

        if contiene_alguno(texto, palabras):
            actividades.append(actividad)

    return actividades


# ============================================================
# INFERENCIA DE POTENCIAL
# ============================================================

def inferir_potencial(texto):

    potenciales = []

    agua_fluvial = contiene_alguno(
        texto,
        INDICADORES["AGUA_FLUVIAL"]
    )

    agua_lacustre = contiene_alguno(
        texto,
        INDICADORES["AGUA_LACUSTRE"]
    )

    mar = contiene_alguno(
        texto,
        INDICADORES["MAR_COSTA"]
    )

    montana = contiene_alguno(
        texto,
        INDICADORES["MONTANA"]
    )

    senderos = contiene_alguno(
        texto,
        INDICADORES["SENDEROS"]
    )

    naturaleza = contiene_alguno(
        texto,
        INDICADORES["NATURALEZA"]
    )

    observacion = contiene_alguno(
        texto,
        INDICADORES["OBSERVACION"]
    )

    acceso = contiene_alguno(
        texto,
        INDICADORES["ACCESO"]
    )

    # --------------------------------------------------------
    # TREKKING / SENDERISMO
    # --------------------------------------------------------

    if senderos and (
        montana
        or naturaleza
        or agua_lacustre
        or agua_fluvial
    ):
        potenciales.append(
            "TREKKING_SENDERISMO"
        )

    # --------------------------------------------------------
    # MONTAÑISMO
    # --------------------------------------------------------

    if montana and senderos:
        potenciales.append(
            "MONTANISMO"
        )

    # --------------------------------------------------------
    # AVENTURA ACUÁTICA FLUVIAL
    # --------------------------------------------------------

    if agua_fluvial and acceso:
        potenciales.append(
            "AVENTURA_ACUATICA_FLUVIAL"
        )

    # --------------------------------------------------------
    # KAYAK / EXPERIENCIAS LACUSTRES
    # --------------------------------------------------------

    if agua_lacustre and acceso:
        potenciales.append(
            "ACTIVIDADES_LACUSTRES"
        )

    # --------------------------------------------------------
    # ACTIVIDADES MARINO-COSTERAS
    # --------------------------------------------------------

    if mar and acceso:
        potenciales.append(
            "ACTIVIDADES_MARINO_COSTERAS"
        )

    # --------------------------------------------------------
    # OBSERVACIÓN DE NATURALEZA
    # --------------------------------------------------------

    if observacion and naturaleza:
        potenciales.append(
            "OBSERVACION_NATURALEZA"
        )

    return sorted(
        set(potenciales)
    )


# ============================================================
# NIVEL DE EVIDENCIA
# ============================================================

def nivel_evidencia(explicitas, inferidas):

    if explicitas:
        return "CONFIRMADO"

    if len(inferidas) >= 2:
        return "PROBABLE"

    if len(inferidas) == 1:
        return "POTENCIAL"

    return "SIN EVIDENCIA"


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():

    print("=" * 95)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("MOTOR DE POTENCIAL DE AVENTURA")
    print("=" * 95)

    df = pd.read_excel(
        ENTRADA,
        sheet_name="Matriz_Impacto"
    )

    print(
        f"\nRegistros cargados: {len(df):,}"
    )

    df["Texto_Potencial"] = (
        df["Proyecto"]
        .fillna("")
        .astype(str)
        .apply(normalizar)
    )

    # --------------------------------------------------------
    # ACTIVIDADES EXPLÍCITAS
    # --------------------------------------------------------

    df["Actividades_Explicitas"] = (
        df["Texto_Potencial"]
        .apply(
            detectar_actividades_explicitas
        )
    )

    # --------------------------------------------------------
    # ACTIVIDADES INFERIDAS
    # --------------------------------------------------------

    df["Actividades_Inferidas"] = (
        df["Texto_Potencial"]
        .apply(
            inferir_potencial
        )
    )

    # --------------------------------------------------------
    # NIVEL DE EVIDENCIA
    # --------------------------------------------------------

    df["Nivel_Evidencia_Aventura"] = (
        df.apply(
            lambda row:
            nivel_evidencia(
                row["Actividades_Explicitas"],
                row["Actividades_Inferidas"]
            ),
            axis=1
        )
    )

    # --------------------------------------------------------
    # VARIABLES BINARIAS
    # --------------------------------------------------------

    df["Es_Confirmado"] = (
        df["Nivel_Evidencia_Aventura"]
        == "CONFIRMADO"
    ).astype(int)

    df["Es_Probable"] = (
        df["Nivel_Evidencia_Aventura"]
        == "PROBABLE"
    ).astype(int)

    df["Es_Potencial"] = (
        df["Nivel_Evidencia_Aventura"]
        == "POTENCIAL"
    ).astype(int)

    # --------------------------------------------------------
    # CONVERTIR LISTAS A TEXTO
    # --------------------------------------------------------

    df["Actividades_Explicitas"] = (
        df["Actividades_Explicitas"]
        .apply(
            lambda x:
            ", ".join(x)
        )
    )

    df["Actividades_Inferidas"] = (
        df["Actividades_Inferidas"]
        .apply(
            lambda x:
            ", ".join(x)
        )
    )

    # ========================================================
    # RESUMEN NACIONAL
    # ========================================================

    resumen = (
        df.groupby(
            "Nivel_Evidencia_Aventura",
            as_index=False
        )
        .agg(
            Registros=("ID_Radar", "count"),
            PIM=("PIM", "sum"),
            Devengado=("Devengado", "sum")
        )
    )

    pim_radar = df["PIM"].sum()

    resumen["Peso_PIM_Radar"] = (
        resumen["PIM"]
        / pim_radar
        * 100
    )

    resumen["Avance_Porcentaje"] = (
        resumen["Devengado"]
        / resumen["PIM"]
        * 100
    ).fillna(0)

    # ========================================================
    # ACTIVIDADES INFERIDAS
    # ========================================================

    actividades_inferidas = [
        "TREKKING_SENDERISMO",
        "MONTANISMO",
        "AVENTURA_ACUATICA_FLUVIAL",
        "ACTIVIDADES_LACUSTRES",
        "ACTIVIDADES_MARINO_COSTERAS",
        "OBSERVACION_NATURALEZA"
    ]

    filas = []

    for actividad in actividades_inferidas:

        mascara = (
            df["Actividades_Inferidas"]
            .str.contains(
                actividad,
                na=False,
                regex=False
            )
        )

        sub = df[mascara]

        filas.append(
            {
                "Actividad_Inferida": actividad,
                "Registros": len(sub),
                "PIM": sub["PIM"].sum(),
                "Devengado": sub["Devengado"].sum()
            }
        )

    resumen_inferido = pd.DataFrame(
        filas
    )

    resumen_inferido["Peso_PIM_Radar"] = (
        resumen_inferido["PIM"]
        / pim_radar
        * 100
    )

    resumen_inferido["Avance_Porcentaje"] = (
        resumen_inferido["Devengado"]
        / resumen_inferido["PIM"]
        * 100
    ).fillna(0)

    resumen_inferido = (
        resumen_inferido
        .sort_values(
            "PIM",
            ascending=False
        )
    )

    # ========================================================
    # MATRIZ TERRITORIAL
    # ========================================================

    territorial = (
        df[
            df["Nivel_Evidencia_Aventura"]
            != "SIN EVIDENCIA"
        ]
        .groupby(
            "Departamento",
            as_index=False
        )
        .agg(
            Registros_Potencial=(
                "ID_Radar",
                "count"
            ),
            PIM_Potencial=(
                "PIM",
                "sum"
            ),
            Devengado_Potencial=(
                "Devengado",
                "sum"
            ),
            Confirmados=(
                "Es_Confirmado",
                "sum"
            ),
            Probables=(
                "Es_Probable",
                "sum"
            ),
            Potenciales=(
                "Es_Potencial",
                "sum"
            )
        )
    )

    territorial["Avance_Potencial"] = (
        territorial["Devengado_Potencial"]
        / territorial["PIM_Potencial"]
        * 100
    ).fillna(0)

    territorial = territorial.sort_values(
        "PIM_Potencial",
        ascending=False
    )

    # ========================================================
    # MOSTRAR RESULTADOS
    # ========================================================

    print("\n" + "=" * 95)
    print("NIVEL DE EVIDENCIA DE AVENTURA")
    print("=" * 95)

    print(
        resumen.to_string(
            index=False,
            formatters={
                "PIM":
                    lambda x: f"{x:,.0f}",
                "Devengado":
                    lambda x: f"{x:,.0f}",
                "Peso_PIM_Radar":
                    lambda x: f"{x:.1f}%",
                "Avance_Porcentaje":
                    lambda x: f"{x:.1f}%"
            }
        )
    )

    print("\n" + "=" * 95)
    print("ACTIVIDADES INFERIDAS")
    print("=" * 95)

    print(
        resumen_inferido.to_string(
            index=False,
            formatters={
                "PIM":
                    lambda x: f"{x:,.0f}",
                "Devengado":
                    lambda x: f"{x:,.0f}",
                "Peso_PIM_Radar":
                    lambda x: f"{x:.1f}%",
                "Avance_Porcentaje":
                    lambda x: f"{x:.1f}%"
            }
        )
    )

    print("\n" + "=" * 95)
    print("TOP 15 TERRITORIOS POR POTENCIAL")
    print("=" * 95)

    print(
        territorial.head(15).to_string(
            index=False,
            formatters={
                "PIM_Potencial":
                    lambda x: f"{x:,.0f}",
                "Devengado_Potencial":
                    lambda x: f"{x:,.0f}",
                "Avance_Potencial":
                    lambda x: f"{x:.1f}%"
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
        f"REGISTROS RADAR : {len(df):,}"
    )

    print(
        f"PIM RADAR       : S/ {df['PIM'].sum():,.0f}"
    )

    print(
        f"DEVENGADO RADAR : S/ {df['Devengado'].sum():,.0f}"
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
            sheet_name="Base_Potencial",
            index=False
        )

        resumen.to_excel(
            writer,
            sheet_name="Nivel_Evidencia",
            index=False
        )

        resumen_inferido.to_excel(
            writer,
            sheet_name="Actividades_Inferidas",
            index=False
        )

        territorial.to_excel(
            writer,
            sheet_name="Territorial_Potencial",
            index=False
        )

    print("\nARCHIVO GENERADO:")
    print(SALIDA)

    print(
        "\n✓ MOTOR DE POTENCIAL DE AVENTURA COMPLETADO"
    )

    print("FIN")


if __name__ == "__main__":
    main()