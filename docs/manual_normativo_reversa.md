# Manual Normativo Interno — Reversa

## Recuperación de fraude en rieles de pago inmediato (Bre-B / Pix)

Versión 1.0 — Documento de operaciones. Fundamenta las recomendaciones del
expediente de cada caso.

---

## 1. Brasil / Pix: el MED como referencia regional

En Brasil, el mecanismo de recuperación post-fraude para Pix es el **MED
(Mecanismo Especial de Devolução)**.

- La recuperación histórica del MED es **baja: aproximadamente el 9–14 % de los
  montos robados**. La causa principal es que la revisión humana pierde la
  carrera de velocidad contra el retiro del dinero (cashout) por parte del
  defraudador.
- **MED 2.0**, de adopción **obligatoria desde febrero de 2026**, mejora el
  mecanismo: rastrea los fondos a través de **hasta 5 capas de cuentas** y
  permite el **bloqueo en cuentas intermedias**, no solo en la cuenta receptora
  inicial.

## 2. Colombia / Bre-B: sin mecanismo equivalente

- **Bre-B es operado por el Banco de la República.**
- **No existe todavía un mecanismo de recuperación equivalente al MED** para
  Bre-B.
- Las disputas se tramitan a través del **servicio al cliente de cada entidad**,
  bajo la vigilancia de la **SFC (Superintendencia Financiera de Colombia)**.

## 3. Flujo de recuperación ISO 20022

El flujo interbancario de bloqueo y devolución se compone de tres mensajes:

1. **camt.056** (*FIToFIPaymentCancellationRequest*), con código de motivo
   **FRAD**: solicita el bloqueo y la devolución (recall) de los fondos a la
   institución que custodia la cuenta receptora.
2. **camt.029** (*ResolutionOfInvestigation*): la institución receptora
   responde **aceptando o rechazando** la solicitud de recall.
3. **pacs.004** (*PaymentReturn*): si el recall es aceptado, la devolución de
   los fondos se liquida mediante este mensaje.

## 4. Guía operativa post-emisión

- Tras emitir el **camt.056**, el caso **permanece abierto a la espera del
  camt.029** de la institución receptora.
- El **SLA recomendado de seguimiento es de 72 horas** desde la emisión del
  camt.056.
- La **institución de la víctima debe formalizar la reclamación ante la
  institución receptora citando el case_id** del caso.
