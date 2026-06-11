"""Emisión de solicitudes de bloqueo/devolución (camt.056) para Reversa.

En el sistema final esto enviará un mensaje ISO 20022 real (validado contra XSD)
al banco que custodia la cuenta. En el prototipo, generamos el mensaje y simulamos
su envío, marcando la cuenta como bloqueada en el grafo en memoria.

La moneda y la zona horaria siguen al riel del caso: BRL/America-Sao_Paulo para
la cadena Pix (Brasil), COP/America-Bogota para la cadena Bre-B (Colombia).
"""

import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from .money_graph import MONEY_GRAPH

_TZ_BY_CURRENCY = {
    "BRL": "America/Sao_Paulo",
    "COP": "America/Bogota",
}


def issue_recall(account_key: str, amount: float) -> dict:
    """Emite una solicitud de bloqueo y devolución de fondos (camt.056) sobre una cuenta.

    Úsala cuando el rastreo indique que los fondos están detenidos e interceptables:
    pásale la llave/chave de la cuenta donde está el dinero (current_location) y el
    monto del fraude. Genera el mensaje camt.056 (FIToFIPaymentCancellationRequest)
    con motivo FRAD y lo envía al banco custodio, congelando los fondos. La moneda
    (COP o BRL) se toma automáticamente del riel de la cuenta.
    """
    node = MONEY_GRAPH.get(account_key)
    if node is None:
        return {"status": "ERROR", "detail": f"La llave {account_key} no existe en el grafo."}

    if node.get("blocked"):
        return {
            "status": "YA BLOQUEADA",
            "account_key": account_key,
            "bank": node["bank"],
            "detail": "Esta cuenta ya tiene un recall emitido previamente.",
        }

    currency = node.get("currency", "COP")
    now = datetime.now(ZoneInfo(_TZ_BY_CURRENCY.get(currency, "America/Bogota")))
    message_id = f"REVERSA-{now:%Y%m%d}-{uuid.uuid4().hex[:8].upper()}"
    case_id = f"CASO-{uuid.uuid4().hex[:8].upper()}"

    camt_056 = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.056.001.08">
  <FIToFIPmtCxlReq>
    <Assgnmt>
      <Id>{message_id}</Id>
      <Assgnr><Agt><FinInstnId><Nm>REVERSA (en nombre del banco de la victima)</Nm></FinInstnId></Agt></Assgnr>
      <Assgne><Agt><FinInstnId><Nm>{node["bank"]}</Nm></FinInstnId></Agt></Assgne>
      <CreDtTm>{now.isoformat()}</CreDtTm>
    </Assgnmt>
    <Case><Id>{case_id}</Id><Cretr><Pty><Nm>REVERSA</Nm></Pty></Cretr></Case>
    <Undrlyg>
      <TxInf>
        <OrgnlIntrBkSttlmAmt Ccy="{currency}">{amount:.2f}</OrgnlIntrBkSttlmAmt>
        <CxlRsnInf><Rsn><Cd>FRAD</Cd></Rsn></CxlRsnInf>
      </TxInf>
    </Undrlyg>
  </FIToFIPmtCxlReq>
</Document>"""

    # Simula el envío: el banco custodio congela la cuenta.
    node["blocked"] = True

    return {
        "status": "BLOQUEO EMITIDO",
        "message_id": message_id,
        "case_id": case_id,
        "account_key": account_key,
        "bank": node["bank"],
        "amount": amount,
        "currency": currency,
        "reason_code": "FRAD",
        "sent_at": now.isoformat(),
        "camt_056": camt_056,
    }
