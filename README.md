# Clasificador de solicitudes

Sistema para clasificar mensajes de soporte al cliente por intención, mostrar confianza de predicción y orientar el enrutamiento operativo. La app web está implementada con Streamlit y consume un modelo SVM calibrado entrenado sobre el dataset limpio y su extensión sintética.

## Arquitectura

- `Sistema_clasificador/app_streamlit.py`: interfaz web, carga del modelo y presentación del resultado.
- `Sistema_clasificador/models/modelo_svm.py`: entrenamiento del modelo principal con TF-IDF + SVM calibrado.
- `herramientas/generar_ejemplos_intencion.py`: crea ejemplos canónicos y sintéticos por intención.
- `herramientas/fusionar_sinteticos.py`: fusiona el dataset original con los sintéticos.
- `herramientas/entrenamiento_base.py`: baseline alternativo con embeddings + clasificador multilabel.
- `herramientas/prediccion_ejemplo.py`: ejemplo simple de inferencia sobre textos nuevos.
- `Sistema_clasificador/data/tabla_intenciones.csv`: catálogo maestro de intenciones, categorías y reglas de actuación.

## Cómo funcionan los modelos de IA

### Modelo principal de producción

El modelo principal está pensado para clasificar un mensaje corto de soporte en una intención concreta. Su funcionamiento es este:

1. El texto entra a la app y se normaliza con limpieza básica: minúsculas, sin URLs, sin correos y con signos de puntuación reducidos.
2. El entrenamiento transforma el texto en características numéricas usando TF-IDF de palabras y de caracteres.
3. Esas características pasan a un SVM lineal calibrado, que no solo decide la intención sino que también produce una probabilidad o confianza aproximada.
4. La app muestra la intención principal, la categoría asociada, la prioridad y una recomendación operativa.
5. También muestra las 3 intenciones más cercanas para apoyar la revisión humana cuando el caso es ambiguo.

El motivo de usar SVM calibrado es que funciona muy bien para clasificación de texto con etiquetas claras y permite obtener una confianza útil para decidir cuándo escalar a revisión manual.

### Modelo baseline de referencia

Además del modelo principal, el repo tiene un baseline de comparación:

1. Toma el texto.
2. Lo convierte en embeddings semánticos con `sentence-transformers`.
3. Entrena un clasificador `OneVsRestClassifier` con `LogisticRegression`.
4. Guarda artefactos reutilizables para pruebas rápidas o evaluación comparativa.

Este baseline sirve para contrastar resultados, no como motor principal de la app.

## Flujo del sistema

1. Se redacta o corrige la taxonomía en `tabla_intenciones.csv`.
2. Se generan ejemplos enriquecidos y sintéticos para las intenciones nuevas o ambiguas.
3. Se fusionan los datos con el dataset limpio para ampliar cobertura.
4. Se entrena o reentrena el modelo SVM.
5. La app Streamlit carga el modelo y la tabla de intenciones para mostrar intención, categoría, prioridad y recomendación.

## Funciones principales

- Clasificación de intención con confianza estimada.
- Visualización de las 3 intenciones más cercanas.
- Recomendación operativa por intención.
- Conteo visible de intenciones y registros usados por la aplicación.

## Ejecutar con Docker

Construir la imagen:

```bash
docker build -t clasificador-de-solicitudes .
```

Ejecutar con Docker:

```bash
docker run -p 8501:8501 clasificador-de-solicitudes
```

O con Docker Compose:

```bash
docker compose up --build
```

La app queda disponible en `http://localhost:8501`.

## Documento relacionado

- [SISTEMA_Y_ETIQUETADO.md](SISTEMA_Y_ETIQUETADO.md): explicación de funcionamiento, jerarquía de intenciones y criterio de etiquetado.
