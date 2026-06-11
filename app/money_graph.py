"""Grafo del dinero simulado para Reversa — dos rieles, un pipeline.

Representa cuentas mula y cómo el dinero salta de una a otra, con una cadena
por riel: Bre-B (Colombia, llaves numéricas, COP) y Pix (Brasil, chaves
CPF/teléfono/EVP, BRL). En el sistema final esto vendrá de datos reales
(PaySim + transacciones Bre-B/Pix); por ahora es un mock en memoria para
construir y demostrar la capacidad de rastreo multi-salto.

Instituciones FICTICIAS en ambos rieles (ningún banco/fintech real).

Nota (LESSONS.md — Estado y demos): el grafo vive en memoria POR PROCESO; un
recall emitido persiste hasta reiniciar ese proceso. Reiniciar para demo limpia.
"""

# Cada llave/chave (cuenta) -> a dónde mandó el dinero ("next").
# next = None significa que el dinero quedó detenido ahí (aún dentro del sistema).
MONEY_GRAPH = {
    # --- Cadena Colombia / Bre-B: llaves numéricas, COP ---
    "3001234567": {"owner": "Cuenta mula 1", "bank": "Banco Andes", "currency": "COP", "next": "3109876543"},
    "3109876543": {"owner": "Cuenta mula 2", "bank": "PagoYa",      "currency": "COP", "next": "3155551234"},
    "3155551234": {"owner": "Cuenta mula 3", "bank": "Banco Andes", "currency": "COP", "next": None},
    # --- Cadeia Brasil / Pix: chave CPF -> chave celular -> chave aleatória (EVP), BRL ---
    "123.456.789-09":  {"owner": "Conta laranja 1", "bank": "Banco Mirante", "currency": "BRL", "next": "+5511987654321"},
    "+5511987654321":  {"owner": "Conta laranja 2", "bank": "ContaZum",         "currency": "BRL", "next": "7f3a9c2e-4b8d-4f6a-9e1c-2d5b8a7c4e3f"},
    "7f3a9c2e-4b8d-4f6a-9e1c-2d5b8a7c4e3f": {"owner": "Conta laranja 3", "bank": "Banco Mirante", "currency": "BRL", "next": None},
}


def trace_funds(destination_key: str) -> dict:
    """Rastrea el recorrido del dinero desde la llave/chave destino de un pago fraudulento.

    Sigue la cadena de cuentas mula salto por salto hasta donde el dinero esté
    detenido. Úsala con la llave_destino del reporte (llave Bre-B o chave Pix,
    tal cual la reportó la víctima) para saber a dónde se movió el dinero y
    dónde está ahora.
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
                "currency": node.get("currency", "COP"),
                "status": status,
            }
        current = node["next"]
    return {"destination_key": destination_key, "path": path, "status": "ciclo detectado"}
