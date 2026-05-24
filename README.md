# Clasificador de solicitudes

Sistema para clasificar mensajes de soporte al cliente por intención y facilitar el enrutamiento operativo.

Componentes clave

- Aplicación web: `Sistema_clasificador/app_streamlit.py` (interfaz y carga del modelo).
- Modelo: `Sistema_clasificador/models/modelo_svm.pkl` (modelo SVM calibrado usado en producción).
- Datos: `Sistema_clasificador/data/` (datasets y tabla `tabla_intenciones.csv`).
- Dependencias: `Sistema_clasificador/requirements.txt`.
- Contenerización: `Dockerfile` y `docker-compose.yml`.

Ejecutar localmente (sin Docker)

```powershell
python -m pip install -r .\Sistema_clasificador\requirements.txt
python -m streamlit run .\Sistema_clasificador\app_streamlit.py
```

Ejecutar con Docker

```bash
docker compose up --build
```

La app estará disponible en `http://localhost:8501`.

Más información técnica: [SISTEMA_Y_ETIQUETADO.md](SISTEMA_Y_ETIQUETADO.md)

---

Información general

Este repositorio contiene una aplicación web (Streamlit) que usa un modelo de aprendizaje automático para detectar la intención en mensajes de soporte al cliente. Está pensada para integrarse en flujos operativos donde la intención determina la categoría, prioridad y la recomendación de acción.

Requisitos mínimos

- Python 3.9+ o Docker instalado.
- Paquetes listados en `Sistema_clasificador/requirements.txt`.

Uso rápido

- Ejecutar localmente (sin Docker):

```powershell
python -m pip install -r .\Sistema_clasificador\requirements.txt
python -m streamlit run .\Sistema_clasificador\app_streamlit.py
```

- Ejecutar con Docker (recomendado para entornos consistentes):

```bash
docker compose up --build
```

Estructura principal

- `Sistema_clasificador/` : código de la app, modelos y datos.
- `herramientas/` : scripts utilitarios para generación y entrenamiento.
- `Dockerfile`, `docker-compose.yml` : configuración para contenerización.

Si necesitas que el README incluya más detalles (p. ej. ejemplos de API, endpoints o instrucciones de despliegue), dime qué prefieres y lo añado.
