from playwright.sync_api import sync_playwright
import pandas as pd
import re

URL = (
    "https://apps5.mineco.gob.pe/transparencia/Navegador/"
    "default.aspx?y=2026&ap=Proyecto"
)

print("RADAR TURISMO PERÚ")
print("TURISMO → AMAZONAS → PROYECTOS\n")

datos = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("1. Abriendo Consulta Amigable...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    iframe = page.locator("iframe, frame").first
    iframe.wait_for(state="attached", timeout=30000)

    frame = iframe.content_frame

    frame.locator(
        "#ctl00_CPH1_DrpYear"
    ).wait_for(timeout=30000)

    # FUNCIÓN
    print("2. Entrando a FUNCIÓN...")

    frame.locator(
        "#ctl00_CPH1_BtnFuncion"
    ).click()

    page.wait_for_timeout(3500)

    # TURISMO
    print("3. Seleccionando TURISMO...")

    fila_turismo = frame.locator(
        "table.Data tr"
    ).filter(
        has_text="09: TURISMO"
    ).first

    fila_turismo.click()

    page.wait_for_timeout(800)

    # DEPARTAMENTO
    print("4. Entrando a DEPARTAMENTO...")

    frame.locator(
        "#ctl00_CPH1_BtnDepartamentoMeta"
    ).click()

    page.wait_for_timeout(3500)

    # AMAZONAS
    print("5. Seleccionando AMAZONAS...")

    fila_amazonas = frame.locator(
        "table.Data tr"
    ).filter(
        has_text="01: AMAZONAS"
    ).first

    fila_amazonas.click()

    page.wait_for_timeout(800)

    # PRODUCTO / PROYECTO
    print("6. Entrando a PRODUCTO/PROYECTO...")

    frame.locator(
        "#ctl00_CPH1_BtnProdProy"
    ).click()

    page.wait_for_timeout(5000)

    print("\n=== PROYECTOS TURÍSTICOS DE AMAZONAS ===\n")

    filas = frame.locator("table.Data tr")

    cantidad = filas.count()

    print("FILAS ENCONTRADAS:", cantidad)
    print()

    for i in range(cantidad):

        fila = filas.nth(i)
        texto = fila.inner_text().strip()

        if not texto:
            continue

        print(texto)

        partes = re.split(r"\s{2,}|\t+", texto)

        partes = [
            x.strip()
            for x in partes
            if x.strip()
        ]

        if len(partes) < 9:
            continue

        concepto = partes[0]
        numeros = partes[-8:]

        try:

            registro = {
                "Departamento": "AMAZONAS",
                "Proyecto": concepto,
                "PIA": int(numeros[0].replace(",", "")),
                "PIM": int(numeros[1].replace(",", "")),
                "Certificacion": int(numeros[2].replace(",", "")),
                "Compromiso_Anual": int(numeros[3].replace(",", "")),
                "Compromiso_Mensual": int(numeros[4].replace(",", "")),
                "Devengado": int(numeros[5].replace(",", "")),
                "Girado": int(numeros[6].replace(",", "")),
                "Avance_Porcentaje": float(
                    numeros[7].replace(",", "")
                )
            }

            datos.append(registro)

        except Exception:
            pass

    browser.close()

# -----------------------------------------
# CREAR EXCEL
# -----------------------------------------

df = pd.DataFrame(datos)

if not df.empty:

    df["Saldo_por_Ejecutar"] = (
        df["PIM"] - df["Devengado"]
    )

    df = df.sort_values(
        "PIM",
        ascending=False
    )

    salida = (
        "outputs/"
        "radar_turismo_proyectos_amazonas_2026.xlsx"
    )

    df.to_excel(
        salida,
        index=False
    )

    print("\nREGISTROS PROCESADOS:", len(df))

    print("\nARCHIVO CREADO:")
    print(salida)

    print("\nTOP PROYECTOS POR PIM:\n")

    print(
        df[
            [
                "Proyecto",
                "PIM",
                "Devengado",
                "Avance_Porcentaje",
                "Saldo_por_Ejecutar"
            ]
        ].head(20)
    )

else:

    print("\nNo se pudieron estructurar los proyectos.")

print("\nFIN")