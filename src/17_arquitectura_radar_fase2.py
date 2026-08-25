from pathlib import Path
import pandas as pd


# ============================================================
# RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ
# ETAPA 17: ARQUITECTURA FASE 2
# COMPETITIVIDAD E IMPACTO
# ============================================================

SALIDA = Path(
    "outputs/radar_fase2_matriz_indicadores_2026.xlsx"
)


# ============================================================
# MATRIZ MAESTRA DE INDICADORES
# ============================================================

INDICADORES = [

    # --------------------------------------------------------
    # PILAR 1 - DEMANDA
    # --------------------------------------------------------

    {
        "Pilar": "DEMANDA",
        "Subpilar": "Visitación",
        "Indicador": "Visitantes a sitios turísticos",
        "Definicion": (
            "Número total de visitantes registrados en sitios "
            "turísticos por departamento."
        ),
        "Unidad": "Visitantes",
        "Fuente": "MINCETUR - Datos Abiertos",
        "Nivel_Geografico": "Departamento / sitio",
        "Periodicidad": "Mensual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "CSV / descarga oficial",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "DEMANDA",
        "Subpilar": "Visitación",
        "Indicador": "Visitantes nacionales",
        "Definicion": (
            "Número de visitantes nacionales registrados "
            "en sitios turísticos."
        ),
        "Unidad": "Visitantes",
        "Fuente": "MINCETUR - Datos Abiertos",
        "Nivel_Geografico": "Departamento / sitio",
        "Periodicidad": "Mensual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "CSV / descarga oficial",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "DEMANDA",
        "Subpilar": "Visitación",
        "Indicador": "Visitantes extranjeros",
        "Definicion": (
            "Número de visitantes extranjeros registrados "
            "en sitios turísticos."
        ),
        "Unidad": "Visitantes",
        "Fuente": "MINCETUR - Datos Abiertos",
        "Nivel_Geografico": "Departamento / sitio",
        "Periodicidad": "Mensual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "CSV / descarga oficial",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "DEMANDA",
        "Subpilar": "Hospedaje",
        "Indicador": "Arribos a establecimientos",
        "Definicion": (
            "Arribos registrados en establecimientos de "
            "hospedaje por departamento."
        ),
        "Unidad": "Arribos",
        "Fuente": "MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Mensual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "Datos abiertos / reporte estadístico",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "DEMANDA",
        "Subpilar": "Hospedaje",
        "Indicador": "Pernoctaciones",
        "Definicion": (
            "Número de noches registradas en establecimientos "
            "de hospedaje por departamento."
        ),
        "Unidad": "Pernoctaciones",
        "Fuente": "MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Mensual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "Datos abiertos / reporte estadístico",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "DEMANDA",
        "Subpilar": "Estadía",
        "Indicador": "Permanencia promedio",
        "Definicion": (
            "Promedio de noches de permanencia por visitante."
        ),
        "Unidad": "Noches",
        "Fuente": "MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Mensual / anual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "Cálculo derivado",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    # --------------------------------------------------------
    # PILAR 2 - NATURALEZA Y AVENTURA
    # --------------------------------------------------------

    {
        "Pilar": "NATURALEZA_Y_AVENTURA",
        "Subpilar": "Recursos",
        "Indicador": "Recursos turísticos naturales inventariados",
        "Definicion": (
            "Número de recursos turísticos naturales "
            "registrados oficialmente."
        ),
        "Unidad": "Recursos",
        "Fuente": "MINCETUR - Inventario Nacional de Recursos Turísticos",
        "Nivel_Geografico": "Departamento / recurso",
        "Periodicidad": "Actualización variable",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "PARCIAL",
        "Metodo_Extraccion": "Descarga / consolidación",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "NATURALEZA_Y_AVENTURA",
        "Subpilar": "ANP",
        "Indicador": "Áreas Naturales Protegidas",
        "Definicion": (
            "Número de ANP con presencia territorial "
            "en cada departamento."
        ),
        "Unidad": "ANP",
        "Fuente": "SERNANP",
        "Nivel_Geografico": "Departamento / ANP",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "PARCIAL",
        "Metodo_Extraccion": "Datos abiertos / shapefile / listado",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "NATURALEZA_Y_AVENTURA",
        "Subpilar": "ANP",
        "Indicador": "Visitantes a ANP",
        "Definicion": (
            "Número de visitantes registrados en áreas "
            "naturales protegidas."
        ),
        "Unidad": "Visitantes",
        "Fuente": "SERNANP / MINCETUR",
        "Nivel_Geografico": "ANP / departamento",
        "Periodicidad": "Mensual / anual",
        "Cobertura_25_Territorios": "MEDIA",
        "Automatizable": "PARCIAL",
        "Metodo_Extraccion": "Descarga / consolidación",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "NATURALEZA_Y_AVENTURA",
        "Subpilar": "Producto",
        "Indicador": "Actividades de aventura identificadas",
        "Definicion": (
            "Número de actividades de aventura confirmadas "
            "o documentadas territorialmente."
        ),
        "Unidad": "Actividades",
        "Fuente": "MINCETUR / gobiernos regionales / clasificación Radar",
        "Nivel_Geografico": "Departamento / destino",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "MEDIA",
        "Automatizable": "PARCIAL",
        "Metodo_Extraccion": "Clasificación semántica + validación",
        "Estado_Dato": "ESTRATÉGICO",
        "Decision": "EVALUAR"
    },

    {
        "Pilar": "NATURALEZA_Y_AVENTURA",
        "Subpilar": "Producto",
        "Indicador": "Diversidad de ecosistemas turísticos",
        "Definicion": (
            "Número de ecosistemas relevantes para productos "
            "de naturaleza y aventura."
        ),
        "Unidad": "Tipos",
        "Fuente": "Radar / MINAM / MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "PARCIAL",
        "Metodo_Extraccion": "Clasificación territorial",
        "Estado_Dato": "ESTRATÉGICO",
        "Decision": "INCLUIR"
    },

    # --------------------------------------------------------
    # PILAR 3 - CONECTIVIDAD
    # --------------------------------------------------------

    {
        "Pilar": "CONECTIVIDAD",
        "Subpilar": "Aérea",
        "Indicador": "Pasajeros aeroportuarios",
        "Definicion": (
            "Movimiento de pasajeros registrado en "
            "aeropuertos del departamento."
        ),
        "Unidad": "Pasajeros",
        "Fuente": "MINCETUR / CORPAC / MTC",
        "Nivel_Geografico": "Aeropuerto / departamento",
        "Periodicidad": "Mensual",
        "Cobertura_25_Territorios": "MEDIA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "CSV / datos abiertos",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "CONECTIVIDAD",
        "Subpilar": "Aérea",
        "Indicador": "Aeropuertos con vuelos comerciales",
        "Definicion": (
            "Número de aeropuertos con operación comercial "
            "regular."
        ),
        "Unidad": "Aeropuertos",
        "Fuente": "MTC / CORPAC",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "PARCIAL",
        "Metodo_Extraccion": "Listado oficial",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "CONECTIVIDAD",
        "Subpilar": "Terrestre",
        "Indicador": "Accesibilidad vial",
        "Definicion": (
            "Indicador territorial de conectividad vial "
            "hacia destinos turísticos."
        ),
        "Unidad": "Índice",
        "Fuente": "MTC",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "MEDIA",
        "Automatizable": "BAJA",
        "Metodo_Extraccion": "Procesamiento geoespacial",
        "Estado_Dato": "COMPLEJO",
        "Decision": "EVALUAR"
    },

    # --------------------------------------------------------
    # PILAR 4 - OFERTA TURÍSTICA
    # --------------------------------------------------------

    {
        "Pilar": "OFERTA_TURISTICA",
        "Subpilar": "Hospedaje",
        "Indicador": "Establecimientos de hospedaje",
        "Definicion": (
            "Número de establecimientos de hospedaje "
            "registrados."
        ),
        "Unidad": "Establecimientos",
        "Fuente": "MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Mensual / anual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "Directorio oficial",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "OFERTA_TURISTICA",
        "Subpilar": "Agencias",
        "Indicador": "Agencias de viajes",
        "Definicion": (
            "Número de agencias de viajes registradas "
            "por departamento."
        ),
        "Unidad": "Agencias",
        "Fuente": "MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Mensual / anual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "Directorio oficial",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "OFERTA_TURISTICA",
        "Subpilar": "Capacidad",
        "Indicador": "Habitaciones disponibles",
        "Definicion": (
            "Número de habitaciones ofertadas en "
            "establecimientos de hospedaje."
        ),
        "Unidad": "Habitaciones",
        "Fuente": "MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Mensual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "Estadística hotelera",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "OFERTA_TURISTICA",
        "Subpilar": "Ocupación",
        "Indicador": "Tasa de ocupabilidad",
        "Definicion": (
            "Porcentaje de ocupación de habitaciones "
            "en establecimientos de hospedaje."
        ),
        "Unidad": "%",
        "Fuente": "MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Mensual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "Datos abiertos",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "OFERTA_TURISTICA",
        "Subpilar": "Especialización",
        "Indicador": "Operadores especializados en naturaleza y aventura",
        "Definicion": (
            "Número de empresas con oferta explícita "
            "de naturaleza y aventura."
        ),
        "Unidad": "Empresas",
        "Fuente": "MINCETUR / gremios / Radar",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "BAJA",
        "Automatizable": "PARCIAL",
        "Metodo_Extraccion": "Clasificación de oferta",
        "Estado_Dato": "ESTRATÉGICO",
        "Decision": "EVALUAR"
    },

    # --------------------------------------------------------
    # PILAR 5 - SEGURIDAD Y GESTIÓN
    # --------------------------------------------------------

    {
        "Pilar": "SEGURIDAD_Y_GESTION",
        "Subpilar": "Riesgo",
        "Indicador": "Capacidad de respuesta a emergencias",
        "Definicion": (
            "Disponibilidad territorial de servicios de "
            "respuesta y atención de emergencias."
        ),
        "Unidad": "Índice",
        "Fuente": "INDECI / MINSA / gobiernos regionales",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "MEDIA",
        "Automatizable": "BAJA",
        "Metodo_Extraccion": "Múltiples fuentes",
        "Estado_Dato": "COMPLEJO",
        "Decision": "EVALUAR"
    },

    {
        "Pilar": "SEGURIDAD_Y_GESTION",
        "Subpilar": "Planificación",
        "Indicador": "Instrumentos de planificación turística",
        "Definicion": (
            "Existencia de instrumentos territoriales "
            "actualizados de planificación turística."
        ),
        "Unidad": "Índice",
        "Fuente": "MINCETUR / gobiernos regionales",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "BAJA",
        "Metodo_Extraccion": "Revisión documental",
        "Estado_Dato": "ESTRATÉGICO",
        "Decision": "EVALUAR"
    },

    {
        "Pilar": "SEGURIDAD_Y_GESTION",
        "Subpilar": "Formalización",
        "Indicador": "Prestadores turísticos formales",
        "Definicion": (
            "Número de prestadores registrados formalmente."
        ),
        "Unidad": "Prestadores",
        "Fuente": "MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "Directorio oficial",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    # --------------------------------------------------------
    # PILAR 6 - MERCADO Y ECONOMÍA
    # --------------------------------------------------------

    {
        "Pilar": "MERCADO_Y_ECONOMIA",
        "Subpilar": "Empleo",
        "Indicador": "Empleo turístico",
        "Definicion": (
            "Número estimado de empleos asociados "
            "a actividades turísticas."
        ),
        "Unidad": "Personas",
        "Fuente": "MINCETUR / INEI",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "Base estadística",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    },

    {
        "Pilar": "MERCADO_Y_ECONOMIA",
        "Subpilar": "Empresas",
        "Indicador": "Empresas vinculadas al turismo",
        "Definicion": (
            "Número de empresas en actividades "
            "económicas relacionadas con turismo."
        ),
        "Unidad": "Empresas",
        "Fuente": "INEI / SUNAT / MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "MEDIA",
        "Automatizable": "PARCIAL",
        "Metodo_Extraccion": "Base estadística",
        "Estado_Dato": "EVALUAR",
        "Decision": "EVALUAR"
    },

    {
        "Pilar": "MERCADO_Y_ECONOMIA",
        "Subpilar": "Gasto",
        "Indicador": "Gasto turístico",
        "Definicion": (
            "Gasto promedio estimado de visitantes "
            "en el territorio."
        ),
        "Unidad": "Soles / USD",
        "Fuente": "PROMPERÚ / MINCETUR",
        "Nivel_Geografico": "Macroregión / departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "BAJA",
        "Automatizable": "BAJA",
        "Metodo_Extraccion": "Encuestas / perfiles",
        "Estado_Dato": "COMPLEJO",
        "Decision": "EVALUAR"
    },

    {
        "Pilar": "MERCADO_Y_ECONOMIA",
        "Subpilar": "Dinamismo",
        "Indicador": "Crecimiento de la demanda turística",
        "Definicion": (
            "Variación interanual de visitantes o arribos."
        ),
        "Unidad": "%",
        "Fuente": "MINCETUR",
        "Nivel_Geografico": "Departamento",
        "Periodicidad": "Anual",
        "Cobertura_25_Territorios": "ALTA",
        "Automatizable": "SI",
        "Metodo_Extraccion": "Cálculo derivado",
        "Estado_Dato": "PRIORITARIO",
        "Decision": "INCLUIR"
    }
]


# ============================================================
# PROCESO
# ============================================================

def main():

    print("=" * 100)
    print("RADAR TURISMO DE NATURALEZA Y AVENTURA - PERÚ")
    print("17 - ARQUITECTURA FASE 2")
    print("=" * 100)

    df = pd.DataFrame(
        INDICADORES
    )

    # --------------------------------------------------------
    # AÑADIR CAMPOS DE GOBERNANZA
    # --------------------------------------------------------

    df["URL_Fuente"] = ""
    df["Año_Disponible"] = ""
    df["Responsable_Validacion"] = ""
    df["Fecha_Ultima_Revision"] = ""
    df["Observaciones"] = ""

    # --------------------------------------------------------
    # ORDENAR
    # --------------------------------------------------------

    orden_pilares = {
        "DEMANDA": 1,
        "NATURALEZA_Y_AVENTURA": 2,
        "CONECTIVIDAD": 3,
        "OFERTA_TURISTICA": 4,
        "SEGURIDAD_Y_GESTION": 5,
        "MERCADO_Y_ECONOMIA": 6
    }

    df["Orden_Pilar"] = (
        df["Pilar"]
        .map(
            orden_pilares
        )
    )

    df = (
        df
        .sort_values(
            [
                "Orden_Pilar",
                "Subpilar",
                "Indicador"
            ]
        )
        .reset_index(
            drop=True
        )
    )

    df["ID_Indicador"] = (
        range(
            1,
            len(df) + 1
        )
    )

    # --------------------------------------------------------
    # RESUMEN POR PILAR
    # --------------------------------------------------------

    resumen_pilar = (
        df.groupby(
            "Pilar",
            as_index=False
        )
        .agg(
            Indicadores=(
                "Indicador",
                "count"
            ),
            Incluir=(
                "Decision",
                lambda x:
                (x == "INCLUIR").sum()
            ),
            Evaluar=(
                "Decision",
                lambda x:
                (x == "EVALUAR").sum()
            )
        )
    )

    # --------------------------------------------------------
    # RESUMEN AUTOMATIZACIÓN
    # --------------------------------------------------------

    resumen_auto = (
        df.groupby(
            "Automatizable",
            as_index=False
        )
        .agg(
            Indicadores=(
                "Indicador",
                "count"
            )
        )
    )

    # --------------------------------------------------------
    # PRIORIDAD INICIAL
    # --------------------------------------------------------

    prioridad = df[
        df["Decision"]
        == "INCLUIR"
    ].copy()

    prioridad = prioridad[
        [
            "ID_Indicador",
            "Pilar",
            "Subpilar",
            "Indicador",
            "Fuente",
            "Periodicidad",
            "Cobertura_25_Territorios",
            "Automatizable",
            "Metodo_Extraccion"
        ]
    ]

    # --------------------------------------------------------
    # EXPORTAR
    # --------------------------------------------------------

    SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with pd.ExcelWriter(
        SALIDA,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Matriz_Indicadores",
            index=False
        )

        resumen_pilar.to_excel(
            writer,
            sheet_name="Resumen_Pilares",
            index=False
        )

        resumen_auto.to_excel(
            writer,
            sheet_name="Automatizacion",
            index=False
        )

        prioridad.to_excel(
            writer,
            sheet_name="Indicadores_Prioritarios",
            index=False
        )

    # --------------------------------------------------------
    # CONTROL
    # --------------------------------------------------------

    print("\n" + "=" * 100)
    print("RESUMEN DE ARQUITECTURA")
    print("=" * 100)

    print(
        resumen_pilar.to_string(
            index=False
        )
    )

    print("\n" + "=" * 100)
    print("AUTOMATIZACIÓN")
    print("=" * 100)

    print(
        resumen_auto.to_string(
            index=False
        )
    )

    print("\n" + "=" * 100)
    print("CONTROL")
    print("=" * 100)

    print(
        f"INDICADORES TOTALES : {len(df)}"
    )

    print(
        f"INCLUIR             : "
        f"{(df['Decision'] == 'INCLUIR').sum()}"
    )

    print(
        f"EVALUAR             : "
        f"{(df['Decision'] == 'EVALUAR').sum()}"
    )

    print("\nARCHIVO GENERADO:")
    print(SALIDA)

    print(
        "\n✓ ARQUITECTURA FASE 2 COMPLETADA"
    )

    print("FIN")


if __name__ == "__main__":
    main()