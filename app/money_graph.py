"""Grafo del dinero simulado para Reversa.

Representa cuentas mula y cómo el dinero salta de una a otra. En el sistema final
esto vendrá de datos reales (PaySim + transacciones Bre-B/Pix); por ahora es un
mock en memoria para construir y demostrar la capacidad de rastreo.

Nota (LESSONS.md — Estado y demos): el grafo vive en memoria POR PROCESO; un
recall emitido persiste hasta reiniciar ese proceso. Reiniciar para demo limpia.
"""

# Cada llave (cuenta) -> a dónde mandó el dinero ("next").
# next = None significa que el dinero quedó detenido ahí (aún dentro del sistema).
MONEY_GRAPH = {
    "3001234567": {"owner": "Cuenta mula 1", "bank": "Banco Andes", "next": "3109876543"},
    "3109876543": {"owner": "Cuenta mula 2", "bank": "PagoYa",      "next": "3155551234"},
    "3155551234": {"owner": "Cuenta mula 3", "bank": "Banco Andes", "next": None},
}


def trace_funds(destination_key: str) -> dict:
    """Rastrea el recorrido del dinero desde la llave destino de un pago fraudulento.

    Sigue la cadena de cuentas mula salto por salto hasta donde el dinero esté
    detenido. Úsala con la llave_destino del reporte para saber a dónde se movió
    el dinero y dónde está ahora.
    """
    path = []
    current = destination_key
    visited = set()
    while current and current not in visited:
        visited.add(current)
        node = MONEY_GRAPH.get(current)
        if node is None:
            return {"destination_key": destination_key, "path": path,
                    "status": "cuenta desconocida (fuera del grafo)"}
        path.append({"key": current, "owner": node["owner"], "bank": node["bank"]})
        if node.get("next") is None:
            status = (
                "FONDOS BLOQUEADOS - recall camt.056 ya emitido"
                if node.get("blocked")
                else "FONDOS DETENIDOS - interceptable"
            )
            return {
                "destination_key": destination_key,
                "hops": len(path),
                "path": path,
                "current_location": {"key": current, "owner": node["owner"], "bank": node["bank"]},
                "status": status,
            }
        current = node["next"]
    return {"destination_key": destination_key, "path": path, "status": "ciclo detectado"}
