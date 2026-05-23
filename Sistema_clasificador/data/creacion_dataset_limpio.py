import pandas as pd
import re

# Archivo de entrada
archivo_entrada = "Dataset bitext traducido.csv"

# Archivo de salida limpio
archivo_salida = "dataset_bitext_final_limpio.csv"

# Cargar dataset
df = pd.read_csv(archivo_entrada)

# Verificar columnas necesarias
columnas_necesarias = ["instruction_es", "category", "intent"]

for columna in columnas_necesarias:
    if columna not in df.columns:
        raise ValueError(f"No existe la columna requerida: {columna}")

# Asegurar que sean texto
df["instruction_es"] = df["instruction_es"].fillna("").astype(str)
df["category"] = df["category"].fillna("").astype(str)
df["intent"] = df["intent"].fillna("").astype(str)


def normalizar_placeholders(texto):
    """
    Convierte variables como {{Order Number}} o {{Delivery City}}
    en tokens útiles para el modelo.
    """

    def reemplazar(match):
        contenido = match.group(1).strip().lower()

        if "order" in contenido or "pedido" in contenido:
            return " numero_pedido "
        elif "delivery" in contenido or "city" in contenido or "entrega" in contenido:
            return " ciudad_entrega "
        elif "account" in contenido or "cuenta" in contenido:
            return " tipo_cuenta "
        elif "person" in contenido or "name" in contenido or "persona" in contenido:
            return " nombre_persona "
        elif "currency" in contenido or "symbol" in contenido or "moneda" in contenido:
            return " simbolo_moneda "
        elif "refund" in contenido or "reembolso" in contenido:
            return " monto_reembolso "
        elif "email" in contenido or "correo" in contenido:
            return " correo_electronico "
        elif "phone" in contenido or "telefono" in contenido:
            return " numero_telefono "
        elif "invoice" in contenido or "factura" in contenido:
            return " numero_factura "
        else:
            return " dato_variable "

    texto = re.sub(r"\{\{(.*?)\}\}", reemplazar, texto)

    return texto


def limpiar_texto(texto):
    texto = str(texto)

    # Pasar a minúsculas
    texto = texto.lower()

    # Normalizar variables tipo {{Order Number}}
    texto = normalizar_placeholders(texto)

    # Eliminar URLs
    texto = re.sub(r"http\S+|www\S+", " ", texto)

    # Normalizar correos si aparecen
    texto = re.sub(r"\S+@\S+", " correo_electronico ", texto)

    # Quitar signos y caracteres raros, conservando letras, números, tildes, ñ y guion bajo
    texto = re.sub(r"[^a-záéíóúüñ0-9_\s]", " ", texto)

    # Quitar espacios múltiples
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


# Crear nuevo dataframe limpio
df_limpio = pd.DataFrame()

# La nueva columna instruction será la versión en español limpia
df_limpio["instruction"] = df["instruction_es"].apply(limpiar_texto)

# Mantener category e intent
df_limpio["category"] = df["category"]
df_limpio["intent"] = df["intent"]

# Eliminar filas vacías por seguridad
df_limpio = df_limpio[df_limpio["instruction"].str.strip() != ""]

# Guardar archivo final
df_limpio.to_csv(archivo_salida, index=False, encoding="utf-8-sig")

print("Limpieza finalizada.")
print("Archivo guardado como:", archivo_salida)

print("\nTotal de registros:", len(df_limpio))
print("Cantidad de categorías:", df_limpio["category"].nunique())
print("Cantidad de intenciones:", df_limpio["intent"].nunique())

print("\nRegistros por intención:")
print(df_limpio["intent"].value_counts())

print("\nVista previa:")
print(df_limpio.head(10))