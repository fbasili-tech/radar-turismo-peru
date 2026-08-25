import requests
import pandas as pd

BASE = "https://apps5.mineco.gob.pe/transparencia/Navegador/"

urls_prueba = {
    "total": (
        BASE +
        "Navegar_7.aspx?"
        "_tgt=xls&_uhc=yes&0=&y=2026&ap=Proyecto"
        "&cpage=1&psize=400"
    ),

    "funcion_prueba_1": (
        BASE +
        "Navegar_7.aspx?"
        "_tgt=xls&_uhc=yes&0=&y=2026&ap=Proyecto"
        "&dim=Funcion"
        "&cpage=1&psize=400"
    ),

    "funcion_prueba_2": (
        BASE +
        "Navegar_7.aspx?"
        "_tgt=xls&_uhc=yes&0=&y=2026&ap=Proyecto"
        "&d=Funcion"
        "&cpage=1&psize=400"
    )
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("RADAR TURISMO PERÚ")
print("Buscando acceso directo a la dimensión FUNCIÓN\n")

for nombre, url in urls_prueba.items():

    print("=" * 70)
    print("PRUEBA:", nombre)

    r = requests.get(
        url,
        headers=headers,
        timeout=60
    )

    print("ESTADO:", r.status_code)
    print("TAMAÑO:", len(r.content))
    print("TIPO:", r.headers.get("Content-Type"))

    archivo = f"data/{nombre}.xls"

    with open(archivo, "wb") as f:
        f.write(r.content)

    try:
        tablas = pd.read_html(
            archivo,
            encoding="windows-1252"
        )

        print("TABLAS:", len(tablas))

        if len(tablas) >= 3:

            datos = tablas[-1]

            print("FILAS:", len(datos))
            print("\nPRIMERAS FILAS:")
            print(datos.head(10))

    except Exception as e:

        print("NO SE PUDO LEER:")
        print(e)

    print()

print("FIN")