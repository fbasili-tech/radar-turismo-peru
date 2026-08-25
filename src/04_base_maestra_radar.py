from pathlib import Path
import pandas as pd
import re

ENTRADA = Path("outputs/radar_turismo_proyectos_peru_2026.xlsx")
SALIDA = Path("outputs/radar_turismo_base_maestra_2026.xlsx")

CODIGOS_AGREGADOS = {
    2000291: "INFRAESTRUCTURA TURISTICA",
    2001621: "ESTUDIOS DE PRE-INVERSION"
}


def limpiar_proyecto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor)

    # En algunas extracciones el resto de la fila quedó
    # incorporado al nombre después de una tabulación.
    texto = texto.split("\t")[0]

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def main():

    print("=" * 80)
    print("RADAR TURISMO NATURALEZA Y AVENTURA - PERÚ")
    print("CONSTRUCCIÓN DE BASE MAESTRA")
    print("=" * 80)

    df = pd.read_excel(ENTRADA)

    print(f"\nRegistros originales: {len(df):,}")

    # ------------------------------------------------------
    # LIMPIAR NOMBRE DEL PROYECTO
    # ------------------------------------------------------

    df["Proyecto"] = df["Proyecto"].apply(limpiar_proyecto)

    # ------------------------------------------------------
    # IDENTIFICAR REGISTROS AGREGADOS DEL MEF
    # ------------------------------------------------------

    df["Tipo_Registro"] = "PROYECTO INDIVIDUAL"

    for codigo, nombre in CODIGOS_AGREGADOS.items():

        mascara = (
            pd.to_numeric(
                df["Codigo_Proyecto"],
                errors="coerce"
            ) == codigo
        )

        df.loc[mascara, "Tipo_Registro"] = "AGREGADO MEF"
        df.loc[mascara, "Proyecto"] = nombre

    # ------------------------------------------------------
    # CREAR IDENTIFICADOR ÚNICO DEL RADAR
    # ------------------------------------------------------
    #
    # Para proyectos normales usamos el CUI.
    #
    # Para agregados MEF usamos:
    # código + departamento
    #
    # Así no confundimos registros presupuestales diferentes.
    # ------------------------------------------------------

    def crear_id(row):

        codigo = str(row["Codigo_Proyecto"]).replace(".0", "")

        if row["Tipo_Registro"] == "AGREGADO MEF":

            departamento = (
                str(row["Departamento"])
                .upper()
                .strip()
                .replace(" ", "_")
            )

            return f"{codigo}_{departamento}"

        return codigo

    df["ID_Radar"] = df.apply(crear_id, axis=1)

    # ------------------------------------------------------
    # CONTROLES
    # ------------------------------------------------------

    registros = len(df)

    ids_unicos = df["ID_Radar"].nunique()

    duplicados_radar = df.duplicated(
        subset=["ID_Radar"]
    ).sum()

    proyectos_individuales = (
        df["Tipo_Registro"] == "PROYECTO INDIVIDUAL"
    ).sum()

    agregados = (
        df["Tipo_Registro"] == "AGREGADO MEF"
    ).sum()

    pim = df["PIM"].sum()
    devengado = df["Devengado"].sum()

    print("\n" + "=" * 80)
    print("CONTROL DE INTEGRIDAD")
    print("=" * 80)

    print(f"\nREGISTROS PRESUPUESTALES : {registros:,}")
    print(f"ID RADAR ÚNICOS          : {ids_unicos:,}")
    print(f"DUPLICADOS ID RADAR      : {duplicados_radar:,}")

    print(f"\nPROYECTOS INDIVIDUALES   : {proyectos_individuales:,}")
    print(f"REGISTROS AGREGADOS MEF  : {agregados:,}")

    print("\nCONTROL PRESUPUESTAL")

    print(f"PIM TOTAL       : S/ {pim:,.0f}")
    print(f"DEVENGADO TOTAL : S/ {devengado:,.0f}")

    # ------------------------------------------------------
    # RESUMEN DE AGREGADOS
    # ------------------------------------------------------

    agregados_df = df[
        df["Tipo_Registro"] == "AGREGADO MEF"
    ].copy()

    print("\nREGISTROS AGREGADOS IDENTIFICADOS:")

    resumen_agregados = (
        agregados_df
        .groupby(
            ["Codigo_Proyecto", "Proyecto"],
            as_index=False
        )
        .agg(
            Registros=("ID_Radar", "count"),
            PIM=("PIM", "sum"),
            Devengado=("Devengado", "sum")
        )
    )

    print(resumen_agregados.to_string(index=False))

    # ------------------------------------------------------
    # GUARDAR BASE MAESTRA
    # ------------------------------------------------------

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
            sheet_name="Base_Maestra",
            index=False
        )

        agregados_df.to_excel(
            writer,
            sheet_name="Agregados_MEF",
            index=False
        )

        resumen_agregados.to_excel(
            writer,
            sheet_name="Resumen_Agregados",
            index=False
        )

    print("\n" + "=" * 80)

    if duplicados_radar == 0:
        print("✓ BASE MAESTRA SIN DUPLICADOS DE ID RADAR")
    else:
        print("⚠ REVISAR DUPLICADOS DE ID RADAR")

    print("\nARCHIVO CREADO:")
    print(SALIDA)

    print("\nFIN")


if __name__ == "__main__":
    main()