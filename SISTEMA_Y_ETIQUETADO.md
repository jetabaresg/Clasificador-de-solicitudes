# Sistema y etiquetado

Este documento explica cómo funciona el clasificador, cómo quedó organizada la jerarquía de intenciones y qué criterio se siguió para enriquecer el sistema.

## Funcionamiento general

1. El mensaje del cliente entra en la app Streamlit.
2. El texto se limpia con normalización básica.
3. El modelo SVM calibrado predice la intención y estima confianza.
4. La interfaz muestra la intención principal, la categoría técnica, la categoría amigable, la prioridad y la recomendación operativa.
5. También se muestran las 3 intenciones más cercanas para apoyar la revisión humana.

## Jerarquía de intenciones

La jerarquía se organiza en tres niveles prácticos:

- Nivel 1: categoría amplia, por ejemplo `Pedidos`, `Pagos`, `Envíos y logística`, `Cuentas de usuario`.
- Nivel 2: intención concreta, por ejemplo `cancel_order`, `track_refund`, `delivery_not_received`.
- Nivel 3: recomendación operativa, que indica qué hacer con el caso.

Este enfoque evita mezclar etiquetas muy parecidas y permite una respuesta más accionable.

## Criterio de etiquetado

- Usar una sola intención si el mensaje expresa una acción concreta.
- Fusionar etiquetas solo si la diferencia no cambia la acción operativa.
- Separar casos de solicitud y seguimiento cuando la intención sea distinta.
- Priorizar la intención más específica disponible.
- Cuando falten ejemplos reales, generar sintéticos para ampliar cobertura, pero sin inventar clases sin respaldo operativo.

## Recomendaciones operativas

- Mantener las intenciones actuales como base operativa.
- Añadir nuevas etiquetas solo cuando aparezcan suficientes ejemplos reales.
- Revisar periódicamente solapes entre intenciones parecidas.
