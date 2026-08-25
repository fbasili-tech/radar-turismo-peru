from playwright.sync_api import sync_playwright
import pandas as pd
import re

URL = (
    "https://apps5.mineco.gob.pe/transparencia/Navegador/"
    "default.aspx?y=2026&ap=Proyecto"
)

DEPARTAMENTOS = [
    ("01", "AMAZONAS"),
    ("02", "ANCASH"),
    ("03", "APURIMAC"),
    ("04", "AREQUIPA"),
    ("05", "AYACUCHO"),
    ("06", "CAJAMARCA"),
    ("07", "PROVINCIA CONSTITUCIONAL DEL CALLAO"),
    ("08", "CUSCO"),
    ("09", "HUANCAVELICA"),
    ("10", "HUANUCO"),
    ("11", "ICA"),
    ("12", "JUNIN"),
    ("13", "LA LIBERTAD"),
    ("14", "LAMBAYEQUE"),
    ("15", "LIMA"),
    ("16", "LORETO"),
    ("17", "MADRE DE DIOS"),
    ("18", "MOQUEGUA"),
    ("19", "PASCO"),
    ("20", "PIURA"),
    ("21", "PUNO"),
    ("22", "SAN MARTIN"),
    ("23", "TACNA"),
    ("24", "TUMBES"),
    ("25", "UCAYALI"),
]

PIM_NACIONAL_CONTROL = 428_940_955
DEVENGADO_NACIONAL_CONTROL = 205_074_982

registros = []

print("=" * 80)
print("RADAR TURISMO PERÚ")
print("MEF 2026 - PROYECTOS TURÍSTICOS NACIONALES")
print("=" * 80)


def convertir_entero(valor):
    return int(valor.replace(",", "").strip())


def abrir_mef(page):

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    iframe = page.locator("iframe, frame").first
    iframe.wait_for(
        state="attached",
        timeout=30000
    )

    frame = iframe.content_frame

    frame.locator(
        "#ctl00_CPH1_DrpYear"
    ).wait_for(timeout=30000)

    return frame


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    for indice, (codigo_dep, nombre_dep) in enumerate(
        DEPARTAMENTOS,
        start=1
    ):

        print("\n" + "=" * 80)
        print(
            f"{indice}/{len(DEPARTAMENTOS)} "
            f"PROCESANDO: {nombre_dep}"
        )
        print("=" * 80)

        try:

            # =========================================
            # REINICIAR CONSULTA
            # =========================================

            frame = abrir_mef(page)

            print("  → Función")

            frame.locator(
                "#ctl00_CPH1_BtnFuncion"
            ).click()

            page.wait_for_timeout(2500)

            # =========================================
            # TURISMO
            # =========================================

            turismo = frame.locator(
                "table.Data tr"
            ).filter(
                has_text="09: TURISMO"
            ).first

            turismo.wait_for(
                timeout=20000
            )

            radio_turismo = turismo.locator(
                'input[name="grp1"]'
            )

            if radio_turismo.count() > 0:
                radio_turismo.click()
            else:
                turismo.click()

            page.wait_for_timeout(700)

            print("  → 09: TURISMO seleccionado")

            # =========================================
            # DEPARTAMENTO
            # =========================================

            frame.locator(
                "#ctl00_CPH1_BtnDepartamentoMeta"
            ).click()

            page.wait_for_timeout(2500)

            etiqueta = (
                f"{codigo_dep}: {nombre_dep}"
            )

            print(
                "  → Departamento:",
                etiqueta
            )

            fila_dep = frame.locator(
                "table.Data tr"
            ).filter(
                has_text=etiqueta
            ).first

            fila_dep.wait_for(
                timeout=20000
            )

            # Selección explícita
            radio_dep = fila_dep.locator(
                'input[name="grp1"]'
            )

            if radio_dep.count() == 0:

                print(
                    "  ✗ No se encontró radio button."
                )
                continue

            radio_dep.click()

            page.wait_for_timeout(800)

            if not radio_dep.is_checked():

                print(
                    "  ✗ El departamento no quedó "
                    "seleccionado."
                )
                continue

            print(
                "  ✓ Departamento seleccionado"
            )

            # =========================================
            # PRODUCTO / PROYECTO
            # =========================================

            frame.locator(
                "#ctl00_CPH1_BtnProdProy"
            ).click()

            page.wait_for_timeout(3000)

            # =========================================
            # VERIFICAR HISTORIAL
            # =========================================

            historial = frame.locator(
                "#PnlHistory"
            )

            historial_texto = ""

            if historial.count() > 0:

                historial_texto = (
                    historial.inner_text()
                    .upper()
                    .strip()
                )

            if (
                historial_texto
                and nombre_dep.upper()
                not in historial_texto
            ):

                print(
                    "  ✗ El historial del MEF "
                    "no confirma el departamento."
                )

                print(
                    "  Historial:",
                    historial_texto
                )

                continue

            # =========================================
            # LEER PROYECTOS
            # =========================================

            filas = frame.locator(
                "table.Data tr"
            )

            cantidad = filas.count()

            print(
                "  Filas encontradas:",
                cantidad
            )

            procesados = 0

            for i in range(cantidad):

                texto = (
                    filas.nth(i)
                    .inner_text()
                    .strip()
                )

                if not texto:
                    continue

                if texto.startswith(
                    "Sistema de Seguimiento"
                ):
                    continue

                # Proyecto debe comenzar con código
                match = re.match(
                    r"^(\d+):\s*(.+)",
                    texto,
                    re.DOTALL
                )

                if not match:
                    continue

                codigo_proyecto = (
                    match.group(1)
                    .strip()
                )

                resto = (
                    match.group(2)
                    .strip()
                )

                # Extraer números del final
                valores = re.findall(
                    r"(?<!\d)"
                    r"\d{1,3}(?:,\d{3})*"
                    r"(?:\.\d+)?"
                    r"(?!\d)",
                    resto
                )

                if len(valores) < 8:

                    print(
                        "    ⚠ No se pudo interpretar:",
                        codigo_proyecto
                    )

                    continue

                numeros = valores[-8:]

                # Detectar inicio de cifras presupuestales
                pos = resto.rfind(
                    numeros[0]
                )

                nombre_proyecto = (
                    resto[:pos]
                    .strip()
                )

                try:

                    registro = {
                        "Departamento":
                            nombre_dep,

                        "Codigo_Departamento":
                            codigo_dep,

                        "Codigo_Proyecto":
                            codigo_proyecto,

                        "Proyecto":
                            nombre_proyecto,

                        "PIA":
                            convertir_entero(
                                numeros[0]
                            ),

                        "PIM":
                            convertir_entero(
                                numeros[1]
                            ),

                        "Certificacion":
                            convertir_entero(
                                numeros[2]
                            ),

                        "Compromiso_Anual":
                            convertir_entero(
                                numeros[3]
                            ),

                        "Compromiso_Mensual":
                            convertir_entero(
                                numeros[4]
                            ),

                        "Devengado":
                            convertir_entero(
                                numeros[5]
                            ),

                        "Girado":
                            convertir_entero(
                                numeros[6]
                            ),

                        "Avance_Porcentaje":
                            float(
                                numeros[7]
                                .replace(",", "")
                            )
                    }

                    registro[
                        "Saldo_por_Ejecutar"
                    ] = (
                        registro["PIM"]
                        - registro["Devengado"]
                    )

                    registros.append(
                        registro
                    )

                    procesados += 1

                except Exception as e:

                    print(
                        "    ⚠ Error en proyecto",
                        codigo_proyecto,
                        ":",
                        e
                    )

            print(
                "  PROYECTOS PROCESADOS:",
                procesados
            )

        except Exception as e:

            print(
                "  ERROR EN",
                nombre_dep,
                ":",
                e
            )

            continue

    browser.close()


# ==================================================
# CREAR DATAFRAME
# ==================================================

print("\n" + "=" * 80)
print("CONSTRUYENDO BASE NACIONAL")
print("=" * 80)

df = pd.DataFrame(
    registros
)

print(
    "REGISTROS TOTALES:",
    len(df)
)

if df.empty:

    print(
        "No se obtuvieron proyectos."
    )

    raise SystemExit


# ==================================================
# ELIMINAR DUPLICADOS
# ==================================================

antes = len(df)

df = df.drop_duplicates(
    subset=[
        "Departamento",
        "Codigo_Proyecto"
    ]
)

print(
    "Duplicados eliminados:",
    antes - len(df)
)


# ==================================================
# ORDENAR
# ==================================================

df = df.sort_values(
    [
        "Departamento",
        "PIM"
    ],
    ascending=[
        True,
        False
    ]
)


# ==================================================
# RESUMEN DEPARTAMENTAL
# ==================================================

resumen = (
    df.groupby(
        "Departamento",
        as_index=False
    )
    .agg(
        Proyectos=(
            "Codigo_Proyecto",
            "count"
        ),
        PIA=(
            "PIA",
            "sum"
        ),
        PIM=(
            "PIM",
            "sum"
        ),
        Certificacion=(
            "Certificacion",
            "sum"
        ),
        Devengado=(
            "Devengado",
            "sum"
        ),
        Girado=(
            "Girado",
            "sum"
        ),
        Saldo_por_Ejecutar=(
            "Saldo_por_Ejecutar",
            "sum"
        )
    )
)

resumen[
    "Avance_Porcentaje"
] = (
    resumen["Devengado"]
    / resumen["PIM"]
    * 100
).round(1)

resumen = resumen.sort_values(
    "PIM",
    ascending=False
)


# ==================================================
# CONTROLES DE CALIDAD
# ==================================================

pim_calculado = int(
    df["PIM"].sum()
)

devengado_calculado = int(
    df["Devengado"].sum()
)

diferencia_pim = (
    pim_calculado
    - PIM_NACIONAL_CONTROL
)

diferencia_devengado = (
    devengado_calculado
    - DEVENGADO_NACIONAL_CONTROL
)

control = pd.DataFrame(
    [
        {
            "Indicador":
                "PIM",

            "MEF_Control":
                PIM_NACIONAL_CONTROL,

            "Radar_Calculado":
                pim_calculado,

            "Diferencia":
                diferencia_pim
        },
        {
            "Indicador":
                "Devengado",

            "MEF_Control":
                DEVENGADO_NACIONAL_CONTROL,

            "Radar_Calculado":
                devengado_calculado,

            "Diferencia":
                diferencia_devengado
        }
    ]
)


# ==================================================
# BAJA EJECUCIÓN
# ==================================================

baja = df[
    (df["PIM"] > 0)
    &
    (df["Avance_Porcentaje"] < 30)
].copy()

baja = baja.sort_values(
    "PIM",
    ascending=False
)


# ==================================================
# SIN DEVENGADO
# ==================================================

sin_devengado = df[
    (df["PIM"] > 0)
    &
    (df["Devengado"] == 0)
].copy()

sin_devengado = (
    sin_devengado
    .sort_values(
        "PIM",
        ascending=False
    )
)


# ==================================================
# TOP 100
# ==================================================

top100 = (
    df.sort_values(
        "PIM",
        ascending=False
    )
    .head(100)
)


# ==================================================
# GUARDAR EXCEL
# ==================================================

salida = (
    "outputs/"
    "radar_turismo_proyectos_peru_2026.xlsx"
)

with pd.ExcelWriter(
    salida,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Proyectos",
        index=False
    )

    resumen.to_excel(
        writer,
        sheet_name="Resumen_Departamentos",
        index=False
    )

    baja.to_excel(
        writer,
        sheet_name="Baja_Ejecucion",
        index=False
    )

    sin_devengado.to_excel(
        writer,
        sheet_name="Sin_Devengado",
        index=False
    )

    top100.to_excel(
        writer,
        sheet_name="Top_100_PIM",
        index=False
    )

    control.to_excel(
        writer,
        sheet_name="Control_Calidad",
        index=False
    )


# ==================================================
# RESULTADOS
# ==================================================

print("\nARCHIVO CREADO:")
print(salida)

print(
    "\nDEPARTAMENTOS PROCESADOS:",
    df["Departamento"].nunique()
)

print(
    "PROYECTOS:",
    len(df)
)

print("\nPIM CALCULADO:")
print(
    f"S/ {pim_calculado:,.0f}"
)

print("PIM CONTROL MEF:")
print(
    f"S/ {PIM_NACIONAL_CONTROL:,.0f}"
)

print("DIFERENCIA PIM:")
print(
    f"S/ {diferencia_pim:,.0f}"
)

print("\nDEVENGADO CALCULADO:")
print(
    f"S/ {devengado_calculado:,.0f}"
)

print("DEVENGADO CONTROL MEF:")
print(
    f"S/ {DEVENGADO_NACIONAL_CONTROL:,.0f}"
)

print("DIFERENCIA DEVENGADO:")
print(
    f"S/ {diferencia_devengado:,.0f}"
)

if pim_calculado > 0:

    avance = (
        devengado_calculado
        / pim_calculado
        * 100
    )

    print("\nAVANCE NACIONAL:")
    print(
        f"{avance:.1f}%"
    )


print(
    "\nTOP 10 DEPARTAMENTOS POR PIM:\n"
)

print(
    resumen[
        [
            "Departamento",
            "Proyectos",
            "PIM",
            "Devengado",
            "Avance_Porcentaje"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ==================================================
# SEMÁFORO FINAL DE CALIDAD
# ==================================================

print("\n" + "=" * 80)
print("CONTROL DE CALIDAD")
print("=" * 80)

tolerancia = 1000

if (
    abs(diferencia_pim) <= tolerancia
    and
    abs(diferencia_devengado) <= tolerancia
):

    print(
        "✓ BASE VALIDADA CONTRA EL TOTAL DEL MEF"
    )

else:

    print(
        "⚠ BASE TODAVÍA NO RECONCILIA "
        "CON EL TOTAL DEL MEF"
    )

    print(
        "No usar todavía como cifra oficial."
    )

print("\nFIN DEL RADAR")