import pandas as pd

# 1. Cargar el dataset original
archivo = "Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv"

df = pd.read_csv(archivo)

# 2. Revisar columnas
print("Columnas del dataset:")
print(df.columns)

# 3. Revisar cuántas intenciones hay
print("\nCantidad de intenciones:")
print(df["intent"].nunique())

print("\nRegistros por intención antes del muestreo:")
print(df["intent"].value_counts())

# 4. Tomar 300 registros aleatorios por cada intención
# Reemplaza todo el Paso 4 por esto:
muestra = df.groupby("intent", group_keys=False).sample(n=900, random_state=42)

# 5. Mezclar los registros para que no queden ordenados por intención
muestra = muestra.sample(frac=1, random_state=42).reset_index(drop=True)

# 6. Quedarte solo con las columnas que necesitas
muestra = muestra[["instruction", "category", "intent"]]

# 7. Crear columna vacía para la traducción al español
muestra["instruction_es"] = ""

# 8. Guardar nuevo archivo
muestra.to_csv(
    "bitext_muestra_900_por_intencion.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nMuestra creada correctamente.")
print("Total de registros:", len(muestra))

print("\nRegistros por intención en la muestra:")
print(muestra["intent"].value_counts())