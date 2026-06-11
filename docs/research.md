# The Research Behind Reversa

> This project did not start from a technology looking for a problem. It started from a domain investigation into instant-payment fraud in Latin America — this document summarizes what we found and why it pointed to an empty, winnable category: **autonomous fraud recovery**. All figures come from public sources (central bank publications and industry reporting); everything in the Reversa demo itself is synthetic.

## 1. The world moved to instant, irrevocable money

Instant payment rails are the fastest-adopted financial infrastructure of the decade: Brazil's **Pix** (2020) became the country's dominant payment method within a few years, India's UPI processes billions of transactions monthly, and dozens of countries now operate or are building similar rails. In 2025 Colombia launched **Bre-B**, operated by Banco de la República, interconnecting the financial system (over two hundred participating institutions) around instant transfers addressed by simple keys ("llaves").

Two properties define these rails — and define the fraud problem:

1. **Speed**: settlement in seconds, 24/7.
2. **Irrevocability**: once settled, the transfer is final. There is no chargeback.

## 2. Fraud adapted faster than defenses

The dominant fraud on instant rails is not card cloning — it is **authorized-push-payment fraud**: the victim is manipulated (phishing, impersonation of banks or relatives) or coerced (in Brazil, the "sequestro relâmpago" — express kidnapping — became infamous precisely because Pix lets a captor drain accounts in minutes) into sending an instant, irrevocable transfer.

The stolen money then runs a well-known playbook: it hops through **layers of mule accounts** (recruited or rented accounts at multiple institutions) within minutes, and **cashes out** — typically to crypto (USDT) or cash — before anyone reviews anything. The race between the victim's report and the cashout is measured in **minutes**.

## 3. Brazil built a recovery mechanism — and it loses the race

Brazil's central bank answered with the **MED (Mecanismo Especial de Devolução)**, launched in November 2021: a standardized procedure for a victim's bank to request the freezing and return of fraudulent Pix transfers, with analysis windows measured in days.

The result is the single most important number in this project: **the MED recovers roughly 9–14% of stolen amounts** (around 13% in recent reporting, and lower across full-year figures). Not because the mechanism is badly designed — but because it runs at **human speed**. By the time a human analyst reviews the case, the money has already layered through mule accounts and left the system. The MED is a recovery mechanism that arrives after the race is over.

Brazil knows this: **MED 2.0** (mandatory since February 2026) extends tracing across up to **five layers** of accounts and allows blocking funds in intermediate accounts — an explicit acknowledgment that recovery is a *tracing-and-speed* problem. It is still triggered and reviewed by humans.

## 4. Colombia is a greenfield

Bre-B launched with **no MED equivalent**. There is no standardized, rail-level recovery mechanism: a defrauded victim depends on their bank's customer service and ordinary complaint channels, under the general oversight of the Superintendencia Financiera (SFC). Disputes move at help-desk speed against a crime that moves at network speed.

This is the strategic insight: in Colombia, an autonomous recovery layer is not competing against an incumbent mechanism — **it is the first mechanism**.

## 5. The category insight: recovery, not prevention

The fraud-tech industry overwhelmingly sells **prevention**: scoring, friction, transaction blocking before the money leaves. Prevention is crowded, and it will never be perfect — social engineering defeats models because the *legitimate account holder* authorizes the payment.

Almost nobody competes in **recovery**: what happens to the money prevention misses. Today that money is written off. Our research says it shouldn't be — it is not *gone*, it is just *faster than the humans chasing it*. The MED's ~13% is not a ceiling on what's recoverable; it is a measurement of human latency.

## 6. Why autonomous agents, and why now

Recovery decomposes into exactly the loop agents are good at:

- **Understand** an unstructured victim report (intake) →
- **Investigate** by following money across a graph of accounts, enriched with institutional memory of known mules (tracing) →
- **Act** inside the live window by issuing the standardized ISO 20022 recall — **camt.056** (FIToFIPaymentCancellationRequest, reason code FRAD), answered by **camt.029** (resolution) and settled by **pacs.004** (return) →
- **Document** the case in an auditable, regulator-ready dossier (evidence).

Every step is standardized (ISO 20022 is the lingua franca of both Pix messaging and modern rails), every step is machine-readable, and the only thing missing was an actor fast enough to run the loop inside the window. That actor now exists.

Reversa is the implementation of this research: a multi-agent system that collapses the recovery window from days to seconds, learns the mule network across cases, and plugs into a bank's agent ecosystem through the A2A protocol — Colombia-first (where no mechanism exists), Brazil-portable (where the mechanism exists and underperforms), and rail-agnostic by design.

---

*Synthetic-data note: all accounts, institutions ("Banco Andes", "PagoYa"), keys, and transactions in the Reversa demo are fictional. The research above informed the system's design; none of its real-world data flows into the demo.*
