import pandas as pd
import joblib
import re
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# ==============================
# 1. Cargar dataset limpio
# ==============================
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

archivo_merged = PROJECT_DIR / "data" / "dataset_with_synthetic.csv"
archivo_limpio = PROJECT_DIR / "data" / "dataset_bitext_final_limpio.csv"
archivo = archivo_merged if archivo_merged.exists() else archivo_limpio
df = pd.read_csv(archivo)

print("Columnas del dataset:")
print(df.columns)

print("\nTotal de registros:", len(df))
print("Cantidad de intenciones:", df["intent"].nunique())

print("\nRegistros por intención:")
print(df["intent"].value_counts())

# ==============================
# 2. Limpieza del texto
# ==============================

def limpiar_texto(texto):
    texto = str(texto).lower()

    # Eliminar URLs
    texto = re.sub(r"http\S+|www\S+", " ", texto)

    # Normalizar correos
    texto = re.sub(r"\S+@\S+", " correo_electronico ", texto)

    # Quitar signos raros, conservando letras, números, tildes, ñ y guion bajo
    texto = re.sub(r"[^a-záéíóúüñ0-9_\s]", " ", texto)

    # Quitar espacios múltiples
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto

df["instruction"] = df["instruction"].fillna("").astype(str).apply(limpiar_texto)
df["intent"] = df["intent"].fillna("").astype(str)

# Eliminar registros vacíos por seguridad
df = df[df["instruction"].str.strip() != ""]

# ==============================
# 3. Definir entrada y salida
# ==============================

X = df["instruction"]
y = df["intent"]

# ==============================
# 4. Separar entrenamiento y prueba
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nRegistros de entrenamiento:", len(X_train))
print("Registros de prueba:", len(X_test))

# ==============================
# 5. Vectorización mejorada
# ==============================

vectorizador = FeatureUnion([
    (
        "word_tfidf",
        TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            max_features=15000,
            min_df=2,
            sublinear_tf=True,
            strip_accents="unicode"
        )
    ),
    (
        "char_tfidf",
        TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            max_features=10000,
            min_df=2,
            sublinear_tf=True,
            strip_accents="unicode"
        )
    )
])

# ==============================
# 6. Crear modelo SVM calibrado
# ==============================

svm_base = LinearSVC(
    C=1.5,
    max_iter=10000
)

svm_calibrado = CalibratedClassifierCV(
    estimator=svm_base,
    method="sigmoid",
    cv=5
)

modelo = Pipeline([
    ("features", vectorizador),
    ("svm", svm_calibrado)
])

# ==============================
# 7. Entrenar modelo
# ==============================

print("\nEntrenando modelo SVM calibrado mejorado...")
modelo.fit(X_train, y_train)

# ==============================
# 8. Evaluar modelo
# ==============================

y_pred = modelo.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy del modelo calibrado mejorado:")
print(round(accuracy, 4))

print("\nReporte de clasificación:")
print(classification_report(y_test, y_pred))

print("\nMatriz de confusión:")
print(confusion_matrix(y_test, y_pred))

# ==============================
# 9. Analizar confianza
# ==============================

probabilidades = modelo.predict_proba(X_test)
confianzas = probabilidades.max(axis=1)

y_test_array = np.array(y_test)
correctas = y_pred == y_test_array

print("\nAnálisis de confianza:")
print("Confianza promedio general:", round(confianzas.mean(), 4))
print("Confianza promedio en aciertos:", round(confianzas[correctas].mean(), 4))

if (~correctas).sum() > 0:
    print("Confianza promedio en errores:", round(confianzas[~correctas].mean(), 4))
else:
    print("No hubo errores en el conjunto de prueba.")

print("\nDistribución de confianza:")
print("Mínima:", round(confianzas.min(), 4))
print("Percentil 25:", round(np.percentile(confianzas, 25), 4))
print("Mediana:", round(np.percentile(confianzas, 50), 4))
print("Percentil 75:", round(np.percentile(confianzas, 75), 4))
print("Máxima:", round(confianzas.max(), 4))

# ==============================
# 10. Guardar modelo
# ==============================

ruta_modelo = BASE_DIR / "modelo_svm.pkl"

joblib.dump(modelo, ruta_modelo)

print("\nModelo guardado como:", ruta_modelo)