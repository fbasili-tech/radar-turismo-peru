import pandas as pd

print("RADAR TURISMO PERÚ")
print("Sistema iniciado correctamente")

datos = {
    "region": ["Cusco", "Áncash", "Madre de Dios"],
    "actividad": ["Trekking", "Montañismo", "Ecoturismo"],
    "indice": [85, 92, 88]
}

df = pd.DataFrame(datos)

print("\nPrimeros datos del Radar:")
print(df)