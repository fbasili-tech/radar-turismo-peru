from playwright.sync_api import sync_playwright
import pandas as pd
import re
import os

URL = (
    "https://apps5.mineco.gob.pe/transparencia/Navegador/"
    "default.aspx?y=2026&ap=Proyecto"
)

ARCHIVO_EXISTENTE = (
    "outputs/radar_turismo_proyectos_peru_2026.xlsx"
)

DEPARTAMENTO = "MOQUEGUA"
CODIGO_DEPARTAMENTO = "18"

PIM_NACIONAL_CONTROL = 428_940_955
DEVENGADO_NACIONAL_CONTROL = 205_074_982

registros_moquegua = []


def convertir_entero(valor):
    return int(valor.replace(",", "").strip())


print("=" * 80)
print("RADAR TURISMO PERÚ")
print("RECUPERACIÓN DE MOQUEGUA")
print("=" * 80)

# ============================================================
# COMPROBAR BASE EXISTENTE
# ============================================================

if not os.path.exists(ARCHIVO_EXISTENTE):
    print("ERROR:")
    print("No existe el archivo nacional:")
    print(ARCHIVO_EXISTENTE)
    raise SystemExit

df_existente = pd.read_excel(
    ARCHIVO_EXISTENTE,
    sheet_name="Proyectos"
)

print(
    "Registros existentes:",
    len(df_existente)
)

print(
    "Departamentos existentes:",
    df_existente["Departamento"].nunique()
)

# Evitar duplicar Moquegua
df_existente = df_existente[
    df_existente["Departamento"].str.upper()
    != DEPARTAMENTO
].copy()


# ============================================================
# EXTRAER MOQUEGUA
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    print("\n1. Abriendo MEF...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    iframe = page.locator(
        "iframe, frame"
    ).first

    iframe.wait_for(
        state="attached",
        timeout=30000
    )

    frame = iframe.content_frame

    frame.locator(
        "#ctl00_CPH1_DrpYear"
    ).wait_for(
        timeout=30000
    )

    # ========================================================
    # FUNCIÓN
    # ========================================================

    print("2. Entrando a FUNCIÓN...")

    frame.locator(
        "#ctl00_CPH1_BtnFuncion"
    ).click()

    page.wait_for_timeout(2500)

    # ========================================================
    # TURISMO
    # ========================================================

    print("3. Seleccionando 09: TURISMO...")

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

    # ========================================================
    # DEPARTAMENTO
    # ========================================================

    print("4. Entrando a DEPARTAMENTO...")

    frame.locator(
        "#ctl00_CPH1_BtnDepartamentoMeta"
    ).click()

    page.wait_for_timeout(2500)

    etiqueta = (
        f"{CODIGO_DEPARTAMENTO}: "
        f"{DEPARTAMENTO}"
    )

    print(
        "5. Seleccionando:",
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

    radio_dep = fila_dep.locator(
        'input[name="grp1"]'
    )

    if radio_dep.count() == 0:
        print(
            "ERROR: no se encontró "
            "el selector de Moquegua."
        )
        browser.close()
        raise SystemExit

    radio_dep.click()

    page.wait_for_timeout(800)

    if not radio_dep.is_checked():
        print(
            "ERROR: Moquegua no quedó seleccionado."
        )
        browser.close()
        raise SystemExit

    print(
        "✓ MOQUEGUA seleccionado correctamente"
    )

    # ========================================================
    # PRODUCTO / PROYECTO
    # ========================================================

    print("6. Entrando a PRODUCTO/PROYECTO...")

    frame.locator(
        "#ctl00_CPH1_BtnProdProy"
    ).click()

    page.wait_for_timeout(3000)

    filas = frame.locator(
        "table.Data tr"
    )

    cantidad = filas.count()

    print(
        "Filas encontradas:",
        cantidad
    )

    # ========================================================
    # LEER PROYECTOS
    # ========================================================

    for i in range(cantidad):

        texto = (
            filas.nth(i)
            .inner_text()
            .strip()
        )

        if not texto:
            continue

        match = re.match(
            r"^(\d+):\s*(.+)",
            texto,
            re.DOTALL
        )

        if not match:
            continue

        codigo_proyecto = (
            match.group(1).strip()
        )

        resto = (
            match.group(2).strip()
        )

        valores = re.findall(
            r"(?<!\d)"
            r"\d{1,3}(?:,\d{3})*"
            r"(?:\.\d+)?"
            r"(?!\d)",
            resto
        )

        if len(valores) < 8:
            continue

        numeros = valores[-8:]

        posicion = resto.rfind(
            numeros[0]
        )

        nombre_proyecto = (
            resto[:posicion].strip()
        )

        try:

            registro = {

                "Departamento":
                    DEPARTAMENTO,

                "Codigo_Departamento":
                    CODIGO_DEPARTAMENTO,

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

            registros_moquegua.append(
                registro
            )

        except Exception as e:

            print(
                "Error proyecto",
                codigo_proyecto,
                e
            )

    browser.close()


# ============================================================
# CONSOLIDAR
# ============================================================

df_moquegua = pd.DataFrame(
    registros_moquegua
)

print(
    "\nProyectos Moquegua:",
    len(df_moquegua)
)

if df_moquegua.empty:

    print(
        "ERROR: no se obtuvieron "
        "proyectos de Moquegua."
    )

    raise SystemExit

print(
    "PIM MOQUEGUA:",
    f"S/ {df_moquegua['PIM'].sum():,.0f}"
)

print(
    "DEVENGADO MOQUEGUA:",
    f"S/ {df_moquegua['Devengado'].sum():,.0f}"
)

# Unir base anterior + Moquegua

df = pd.concat(
    [
        df_existente,
        df_moquegua
    ],
    ignore_index=True
)

df = df.drop_duplicates(
    subset=[
        "Departamento",
        "Codigo_Proyecto"
    ]
)

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


# ============================================================
# RESUMEN
# ============================================================

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


# ============================================================
# INDICADORES
# ============================================================

baja = df[
    (df["PIM"] > 0)
    &
    (df["Avance_Porcentaje"] < 30)
].sort_values(
    "PIM",
    ascending=False
)

sin_devengado = df[
    (df["PIM"] > 0)
    &
    (df["Devengado"] == 0)
].sort_values(
    "PIM",
    ascending=False
)

top100 = df.sort_values(
    "PIM",
    ascending=False
).head(100)


# ============================================================
# CONTROL DE CALIDAD
# ============================================================

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
            "Indicador": "PIM",

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


# ============================================================
# REESCRIBIR EXCEL NACIONAL
# ============================================================

with pd.ExcelWriter(
    ARCHIVO_EXISTENTE,
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


# ============================================================
# RESULTADO FINAL
# ============================================================

print("\n" + "=" * 80)
print("BASE NACIONAL ACTUALIZADA")
print("=" * 80)

print(
    "DEPARTAMENTOS:",
    df["Departamento"].nunique()
)

print(
    "PROYECTOS:",
    len(df)
)

print("\nPIM NACIONAL:")
print(
    f"S/ {pim_calculado:,.0f}"
)

print("PIM MEF:")
print(
    f"S/ {PIM_NACIONAL_CONTROL:,.0f}"
)

print("DIFERENCIA:")
print(
    f"S/ {diferencia_pim:,.0f}"
)

print("\nDEVENGADO NACIONAL:")
print(
    f"S/ {devengado_calculado:,.0f}"
)

print("DEVENGADO MEF:")
print(
    f"S/ {DEVENGADO_NACIONAL_CONTROL:,.0f}"
)

print("DIFERENCIA:")
print(
    f"S/ {diferencia_devengado:,.0f}"
)

print("\n" + "=" * 80)
print("CONTROL FINAL")
print("=" * 80)

if (
    abs(diferencia_pim) <= 1000
    and
    abs(diferencia_devengado) <= 1000
):

    print(
        "✓ BASE NACIONAL VALIDADA"
    )

else:

    print(
        "⚠ LA BASE TODAVÍA REQUIERE REVISIÓN"
    )

print("\nFIN")