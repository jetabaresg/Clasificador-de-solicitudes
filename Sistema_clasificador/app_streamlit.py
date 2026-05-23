import streamlit as st
import pandas as pd
import joblib
import re
from pathlib import Path

# ==============================
# Configuración general
# ==============================

st.set_page_config(
    page_title="Clasificador de solicitudes",
    page_icon="🤖",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

MODELO_PATH = BASE_DIR / "models" / "modelo_svm.pkl"
FALLBACK_DATASET = BASE_DIR / "data" / "dataset_bitext_final_limpio.csv"
DATASET_PATH = BASE_DIR / "data" / "dataset_with_synthetic.csv"
if not DATASET_PATH.exists():
    DATASET_PATH = FALLBACK_DATASET
TABLA_PATH = BASE_DIR / "data" / "tabla_intenciones.csv"

UMBRAL_ALTO = 0.60
UMBRAL_BAJO = 0.30


# ==============================
# Cargar archivos
# ==============================

@st.cache_resource
def cargar_modelo():
    return joblib.load(MODELO_PATH)


@st.cache_data
def cargar_datos(dataset_signature, tabla_signature):
    df = pd.read_csv(DATASET_PATH)
    tabla = pd.read_csv(TABLA_PATH)

    intent_a_categoria = (
        df.groupby("intent")["category"]
        .agg(lambda x: x.value_counts().index[0])
        .to_dict()
    )

    info_intenciones = tabla.set_index("intent").to_dict(orient="index")

    return df, tabla, intent_a_categoria, info_intenciones


modelo = cargar_modelo()
dataset_signature = DATASET_PATH.stat().st_mtime if DATASET_PATH.exists() else 0
tabla_signature = TABLA_PATH.stat().st_mtime if TABLA_PATH.exists() else 0
df, tabla_intenciones, intent_a_categoria, info_intenciones = cargar_datos(dataset_signature, tabla_signature)


# ==============================
# Funciones
# ==============================

def limpiar_texto(texto):
    texto = str(texto).lower()
    texto = re.sub(r"http\S+|www\S+", " ", texto)
    texto = re.sub(r"\S+@\S+", " correo_electronico ", texto)
    texto = re.sub(r"[^a-záéíóúüñ0-9_\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def estado_confianza(confianza):
    if confianza >= UMBRAL_ALTO:
        return "Alta confianza", "Clasificación segura", "success"
    elif confianza >= UMBRAL_BAJO:
        return "Confianza media", "Revisión recomendada", "warning"
    else:
        return "Baja confianza", "No hay intención exacta", "error"


def predecir_solicitud(texto_usuario):
    texto_limpio = limpiar_texto(texto_usuario)

    probabilidades = modelo.predict_proba([texto_limpio])[0]
    clases = modelo.named_steps["svm"].classes_

    indices_ordenados = probabilidades.argsort()[::-1]
    indice_principal = indices_ordenados[0]

    intent_predicho = clases[indice_principal]
    confianza = float(probabilidades[indice_principal])

    categoria_tecnica = intent_a_categoria.get(intent_predicho, "No identificada")

    info = info_intenciones.get(intent_predicho, {
        "nombre": intent_predicho,
        "categoria_amigable": "No definida",
        "prioridad": "No definida",
        "area_responsable": "No definida",
        "recomendacion": "No hay recomendación disponible para esta intención."
    })

    top_3 = []
    for indice in indices_ordenados[:3]:
        intent_top = clases[indice]
        confianza_top = float(probabilidades[indice])
        info_top = info_intenciones.get(intent_top, {})

        top_3.append({
            "intencion": info_top.get("nombre", intent_top),
            "etiqueta": intent_top,
            "confianza": confianza_top
        })

    return texto_limpio, intent_predicho, categoria_tecnica, info, confianza, top_3


def mostrar_top3(top_3):
    st.subheader("Intenciones más cercanas")

    for i, item in enumerate(top_3, start=1):
        confianza = float(item["confianza"])
        porcentaje = confianza * 100

        with st.container(border=True):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"**{i}. {item['intencion']}**")
                st.code(item["etiqueta"], language=None)

            with col2:
                st.metric("Confianza", f"{porcentaje:.1f}%")

            st.progress(confianza)


# ==============================
# Encabezado
# ==============================

st.title("🤖 Clasificador de solicitudes")
st.write(
    "Sistema inteligente para detectar automáticamente la intención de una solicitud "
    "de atención al cliente usando **NLP + TF-IDF + SVM calibrado**."
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Intenciones", len(tabla_intenciones))

with col2:
    st.metric("Registros", f"{len(df):,}")

with col3:
    st.metric("Umbral alto", f"{int(UMBRAL_ALTO * 100)}%")

with col4:
    st.metric("Umbral bajo", f"{int(UMBRAL_BAJO * 100)}%")

st.divider()


# ==============================
# Entrada
# ==============================

st.subheader("Ingresar solicitud")

solicitud = st.text_area(
    "Escriba aquí el mensaje del cliente:",
    placeholder="Ejemplo: Tengo un problema con el pago...",
    height=120
)

clasificar = st.button("Clasificar solicitud", use_container_width=True)


# ==============================
# Resultado
# ==============================

if clasificar:
    if solicitud.strip() == "":
        st.warning("Por favor ingrese una solicitud para clasificar.")
    else:
        texto_limpio, intent, categoria_tecnica, info, confianza, top_3 = predecir_solicitud(solicitud)
        estado, descripcion_estado, tipo_estado = estado_confianza(confianza)

        porcentaje = confianza * 100

        st.divider()
        st.subheader("Resultado")

        if tipo_estado == "success":
            st.success(f"{estado} - {descripcion_estado}")
            prioridad_mostrada = info["prioridad"]
            area_mostrada = info["area_responsable"]
            recomendacion_mostrada = info["recomendacion"]

        elif tipo_estado == "warning":
            st.warning(f"{estado} - {descripcion_estado}")
            prioridad_mostrada = "Revisión manual"
            area_mostrada = info["area_responsable"]
            recomendacion_mostrada = (
                "La solicitud tiene similitud con una intención entrenada, "
                "pero la confianza no es suficientemente alta. Se recomienda "
                "validar manualmente antes de enrutar el caso."
            )

        else:
            st.error(f"{estado} - {descripcion_estado}")
            prioridad_mostrada = "Revisión manual"
            area_mostrada = "Servicio al cliente"
            recomendacion_mostrada = (
                "La solicitud no coincide claramente con las intenciones entrenadas. "
                "Se recomienda revisión manual o ampliar el dataset con ejemplos similares."
            )

        with st.container(border=True):

            with st.container(border=True):
                st.caption("ESTADO DE CLASIFICACIÓN")
                st.write(f"**{descripcion_estado}**")

            col_titulo, col_confianza = st.columns([3, 1])

            with col_titulo:
                st.markdown(f"## {info['nombre']}")
                st.code(intent, language=None)

            with col_confianza:
                st.metric("Confianza", f"{porcentaje:.1f}%")

            st.progress(confianza)

            col_a, col_b = st.columns(2)

            with col_a:
                with st.container(border=True):
                    st.caption("CATEGORÍA TÉCNICA")
                    st.write(f"**{categoria_tecnica}**")

            with col_b:
                with st.container(border=True):
                    st.caption("CATEGORÍA GENERAL")
                    st.write(f"**{info['categoria_amigable']}**")

            col_c, col_d = st.columns(2)

            with col_c:
                with st.container(border=True):
                    st.caption("PRIORIDAD")
                    st.write(f"**{prioridad_mostrada}**")

            with col_d:
                with st.container(border=True):
                    st.caption("ÁREA RESPONSABLE")
                    st.write(f"**{area_mostrada}**")

            with st.container(border=True):
                st.caption("TEXTO PROCESADO")
                st.write(f"`{texto_limpio}`")

            st.markdown("#### Recomendación")
            st.info(recomendacion_mostrada)

        st.divider()

        mostrar_top3(top_3)


# ==============================
# Información técnica
# ==============================

st.divider()

with st.expander("Información técnica del modelo"):
    st.write("**Técnica utilizada:** NLP + TF-IDF + SVM calibrado")
    st.write("**Archivo del modelo:** modelo_svm.pkl")
    st.write("**Dataset:**", DATASET_PATH.name)
    st.write("**Tabla de apoyo:** tabla_intenciones.csv")
    st.write("**Total de registros:**", len(df))
    st.write("**Total de intenciones:**", len(tabla_intenciones))
    st.write("**Umbral alto:**", UMBRAL_ALTO)
    st.write("**Umbral bajo:**", UMBRAL_BAJO)