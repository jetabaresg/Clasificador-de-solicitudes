import streamlit as st
import pandas as pd
import joblib
import re
from datetime import datetime
from pathlib import Path

# ==============================
# Configuración general
# ==============================

st.set_page_config(
    page_title="Clasificador de solicitudes",
    page_icon="◼",
    layout="wide"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;700&display=swap');

    :root {
        --bg: #050608;
        --surface: rgba(18, 20, 24, 0.94);
        --surface-strong: rgba(24, 26, 32, 0.98);
        --line: rgba(255, 255, 255, 0.09);
        --line-strong: rgba(255, 255, 255, 0.16);
        --text: #f4f6f8;
        --muted: #a6adb7;
        --accent: #e8e4dc;
        --accent-2: #8f94ff;
        --accent-glow: rgba(143, 148, 255, 0.18);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(143, 148, 255, 0.14), transparent 30%),
            radial-gradient(circle at top right, rgba(255, 255, 255, 0.07), transparent 26%),
            linear-gradient(180deg, #050608 0%, #090b0f 48%, #050608 100%);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -0.04em;
        color: var(--text);
    }

    p, li, label, span, div {
        color: var(--text);
    }

    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, rgba(24, 26, 32, 0.98), rgba(13, 15, 18, 0.92));
        border: 1px solid var(--line);
        border-radius: 28px;
        padding: 2rem 2rem 1.8rem;
        margin: 0 0 1.5rem 0;
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.42);
    }

    .hero::before {
        content: '';
        position: absolute;
        inset: -1px;
        background: radial-gradient(circle at top right, rgba(143, 148, 255, 0.18), transparent 30%);
        pointer-events: none;
    }

    .hero-eyebrow {
        position: relative;
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        font-size: 0.76rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 0.9rem;
    }

    .hero-eyebrow::before {
        content: '';
        width: 42px;
        height: 1px;
        background: linear-gradient(90deg, var(--accent-2), transparent);
    }

    .hero h1 {
        position: relative;
        margin: 0;
        font-size: clamp(2.1rem, 3.8vw, 3.8rem);
        line-height: 0.95;
    }

    .hero p {
        position: relative;
        max-width: 760px;
        margin: 0.95rem 0 0;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.7;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(24, 26, 32, 0.96), rgba(14, 16, 20, 0.96));
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 1rem 1.1rem;
        box-shadow: 0 18px 36px rgba(0, 0, 0, 0.2);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    [data-testid="stMetricValue"] {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -0.04em;
    }

    [data-testid="stButton"] button {
        background: linear-gradient(135deg, #e8e4dc 0%, #b9beca 100%);
        color: #08090b;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        font-weight: 700;
        padding: 0.78rem 1rem;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.28);
        transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
    }

    [data-testid="stButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 16px 34px rgba(0, 0, 0, 0.34);
        filter: brightness(1.04);
    }

    [data-testid="stTextInput"] input {
        background: rgba(11, 12, 15, 0.96) !important;
        color: var(--text) !important;
        border: 1px solid var(--line) !important;
        border-radius: 16px !important;
        padding: 0.95rem 1rem !important;
        font-size: 15px !important;
        line-height: 1.5 !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    [data-testid="stTextInput"] input:focus {
        border-color: rgba(143, 148, 255, 0.55) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }

    [data-testid="stContainer"] {
        color: var(--text);
    }

    [data-testid="stExpander"] {
        background: rgba(18, 20, 24, 0.82);
        border: 1px solid var(--line);
        border-radius: 18px;
    }

    [data-testid="stExpander"] summary {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
    }

    [data-testid="stInfo"], [data-testid="stWarning"], [data-testid="stError"], [data-testid="stSuccess"] {
        border-radius: 18px;
        border: 1px solid var(--line);
        backdrop-filter: blur(10px);
    }

    [data-testid="stInfo"] { background: rgba(37, 44, 62, 0.66); }
    [data-testid="stWarning"] { background: rgba(72, 54, 18, 0.55); }
    [data-testid="stError"] { background: rgba(79, 24, 28, 0.58); }
    [data-testid="stSuccess"] { background: rgba(20, 58, 41, 0.58); }

    [data-testid="stCodeBlock"] {
        border-radius: 16px;
        border: 1px solid var(--line);
        overflow: hidden;
    }

    pre, code {
        background: rgba(255, 255, 255, 0.03) !important;
        color: #eef1f6 !important;
    }

    hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, #e8e4dc, #8f94ff) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">Clasificador de solicitudes</div>
        <h1>Clasificador de solicitudes</h1>
        <p>Clasifica solicitudes con una respuesta clara, limpia y confiable en segundos.</p>
    </div>
    """,
    unsafe_allow_html=True,
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
    df = pd.read_csv(DATASET_PATH, encoding="utf-8-sig")
    tabla = pd.read_csv(TABLA_PATH, encoding="utf-8-sig")

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


def construir_resultado(solicitud, texto_limpio, intent, categoria_tecnica, info, confianza, top_3):
    estado, descripcion_estado, tipo_estado = estado_confianza(confianza)

    if tipo_estado == "success":
        prioridad_mostrada = info["prioridad"]
        area_mostrada = info["area_responsable"]
        recomendacion_mostrada = info["recomendacion"]
    elif tipo_estado == "warning":
        prioridad_mostrada = "Revisión manual"
        area_mostrada = info["area_responsable"]
        recomendacion_mostrada = (
            "La solicitud tiene similitud con una intención entrenada, pero la confianza no es suficientemente alta. "
            "Se recomienda validar manualmente antes de enrutar el caso."
        )
    else:
        prioridad_mostrada = "Revisión manual"
        area_mostrada = "Servicio al cliente"
        recomendacion_mostrada = (
            "La solicitud no coincide claramente con las intenciones entrenadas. Se recomienda revisión manual o ampliar "
            "el dataset con ejemplos similares."
        )

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "solicitud": solicitud,
        "texto_limpio": texto_limpio,
        "intent": intent,
        "categoria_tecnica": categoria_tecnica,
        "info": info,
        "confianza": confianza,
        "estado": estado,
        "descripcion_estado": descripcion_estado,
        "tipo_estado": tipo_estado,
        "prioridad_mostrada": prioridad_mostrada,
        "area_mostrada": area_mostrada,
        "recomendacion_mostrada": recomendacion_mostrada,
        "top_3": top_3,
    }


def guardar_resultado(resultado):
    st.session_state.setdefault("historial_respuestas", [])
    st.session_state["ultima_respuesta"] = resultado
    historial = st.session_state["historial_respuestas"]
    historial.insert(0, resultado)
    st.session_state["historial_respuestas"] = historial[:10]


def mostrar_resultado(resultado):
    porcentaje = resultado["confianza"] * 100

    st.divider()
    st.subheader("Resultado")

    if resultado["tipo_estado"] == "success":
        st.success(f"{resultado['estado']} - {resultado['descripcion_estado']}")
    elif resultado["tipo_estado"] == "warning":
        st.warning(f"{resultado['estado']} - {resultado['descripcion_estado']}")
    else:
        st.error(f"{resultado['estado']} - {resultado['descripcion_estado']}")

    with st.container(border=True):

        with st.container(border=True):
            st.caption("ESTADO DE CLASIFICACIÓN")
            st.write(f"**{resultado['descripcion_estado']}**")

        col_titulo, col_confianza = st.columns([3, 1])

        with col_titulo:
            st.markdown(f"## {resultado['info']['nombre']}")
            st.code(resultado["intent"], language=None)

        with col_confianza:
            st.metric("Confianza", f"{porcentaje:.1f}%")

        st.progress(resultado["confianza"])

        col_a, col_b = st.columns(2)

        with col_a:
            with st.container(border=True):
                st.caption("CATEGORÍA TÉCNICA")
                st.write(f"**{resultado['categoria_tecnica']}**")

        with col_b:
            with st.container(border=True):
                st.caption("CATEGORÍA GENERAL")
                st.write(f"**{resultado['info']['categoria_amigable']}**")

        col_c, col_d = st.columns(2)

        with col_c:
            with st.container(border=True):
                st.caption("PRIORIDAD")
                st.write(f"**{resultado['prioridad_mostrada']}**")

        with col_d:
            with st.container(border=True):
                st.caption("ÁREA RESPONSABLE")
                st.write(f"**{resultado['area_mostrada']}**")

        with st.container(border=True):
            st.caption("TEXTO PROCESADO")
            st.write(f"`{resultado['texto_limpio']}`")

        st.markdown("#### Recomendación")
        st.info(resultado["recomendacion_mostrada"])

    st.divider()
    mostrar_top3(resultado["top_3"])


if "historial_respuestas" not in st.session_state:
    st.session_state["historial_respuestas"] = []

if "ultima_respuesta" not in st.session_state:
    st.session_state["ultima_respuesta"] = None


# ==============================
# Encabezado
# ==============================

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

with st.form("form_clasificacion", clear_on_submit=True):
    solicitud = st.text_input(
        "Escriba aquí el mensaje del cliente:",
        placeholder="Ejemplo: Tengo un problema con el pago...",
        help="Presiona Enter para clasificar y guardar la respuesta.",
        key="solicitud_input"
    )

    clasificar = st.form_submit_button("Clasificar y guardar", use_container_width=True)


# ==============================
# Resultado
# ==============================

if clasificar:
    if solicitud.strip() == "":
        st.warning("Por favor ingrese una solicitud para clasificar.")
    else:
        texto_limpio, intent, categoria_tecnica, info, confianza, top_3 = predecir_solicitud(solicitud)
        resultado = construir_resultado(
            solicitud,
            texto_limpio,
            intent,
            categoria_tecnica,
            info,
            confianza,
            top_3,
        )
        guardar_resultado(resultado)

if st.session_state["ultima_respuesta"] is not None:
    mostrar_resultado(st.session_state["ultima_respuesta"])

    with st.expander("Respuestas guardadas", expanded=False):
        for item in st.session_state["historial_respuestas"]:
            st.markdown(
                f"""**{item['timestamp']}** - {item['info']['nombre']}  
Confianza: {item['confianza'] * 100:.1f}%  
Solicitud: {item['solicitud']}"""
            )


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