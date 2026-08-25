import requests
from bs4 import BeautifulSoup

print("MÓDULO MEF - RADAR TURISMO PERÚ")

url = "https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx"

headers = {
    "User-Agent": "Mozilla/5.0"
}

respuesta = requests.get(url, headers=headers, timeout=30)

print("Estado de conexión:", respuesta.status_code)
print("Tamaño recibido:", len(respuesta.text), "caracteres")

soup = BeautifulSoup(respuesta.text, "html.parser")

print("Título de la página:")
print(soup.title.string if soup.title else "Sin título")

print("\nPrimeros formularios encontrados:")
formularios = soup.find_all("form")

for i, formulario in enumerate(formularios[:5], start=1):
    print(i, formulario.get("id"), formulario.get("action"))python src\mef_turismo.py
    