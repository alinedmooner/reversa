# Reversa — Research Summary

> The condensed version of the domain investigation that originated this project. Full investigation, with the global comparative landscape of 100+ instant payment systems: **[research-full.md](research-full.md)**. All figures from public sources (central banks, BIS, ECB, ACI Worldwide); everything in the Reversa demo itself is synthetic.

## 1. Money became instant — and final

Instant payment rails are the fastest-adopted financial infrastructure of the decade: **more than 100 jurisdictions** run live systems (the ECB counts **117** as of mid-2025). Brazil's **Pix** moved ~63.4 billion transactions in 2024 — the highest fast-payment usage per capita in the world. In 2025, Colombia launched **Bre-B** (Banco de la República): instant, 24/7, key-addressed transfers across **200+ institutions**, with ~76 million keys registered in its first months. Two properties define all of these rails: **speed** (settlement in seconds) and **irrevocability** (no chargeback). For commerce, features. For fraud, an attack surface.

## 2. The crime runs in minutes

The dominant fraud is **authorized-push-payment (APP)**: the victim is manipulated (phishing, impersonation — Brazil's "golpe do falso parente") or coerced (the infamous "sequestro relâmpago") into sending the transfer themselves. Prevention models structurally underperform here — the rightful owner authorizes the payment. The stolen money then **layers through 2–5 mule accounts** across institutions and **cashes out** (typically USDT or cash) within minutes. The race between the victim's report and the cashout is the whole game.

## 3. Brazil measured the failure: the MED recovers 7%

Brazil built the official answer — the **MED** (Mecanismo Especial de Devolução, 2021): standardized freeze-and-return requests with analysis windows of days. The result is this project's most important number: **the MED recovers only ~7–14% of stolen amounts depending on period and methodology — the BCB's official 2025 figure is 7% of disputed value, with ~89% of refund requests denied** (the money is already gone, or the account closed). Not bad design: **human latency**. **MED 2.0** (mandatory Feb 2, 2026) extends tracing to **five account layers** and allows blocking intermediate accounts — institutional confirmation that recovery is a *multi-hop tracing and speed* problem. But the loop is still human-paced.

## 4. Colombia has nothing

Bre-B launched with **no MED equivalent**: no standardized tracing, no freeze request, no clock. Victims depend on each bank's customer service under SFC oversight — and the SFC cannot order refunds. Disputes move at help-desk speed against a crime that moves at network speed. In Colombia, an autonomous recovery layer is not competing with an incumbent mechanism — **it is the first mechanism**.

## 5. The category: recovery, not prevention

The industry sells prevention; almost nobody competes in **recovery** — the money prevention misses, today written off as lost. The research says it isn't lost; it is *faster than the humans chasing it*. (The UK's mandatory APP reimbursement — 88% of losses repaid in year one — confirms the gap from the other side: reimbursement **socializes the loss**; it does not **recover the money**.)

## 6. Why autonomous agents, why now

Recovery decomposes into exactly the loop agents are built for: **understand** an unstructured report → **investigate** across the account graph with institutional memory of known mules → **act** inside the window via the standardized ISO 20022 recall (**camt.056**/FRAD → **camt.029** resolution → **pacs.004** return) → **document** for the regulator. Every step is standardized and machine-readable; the only missing piece was an actor fast enough — and auditable enough — to run it. That actor now exists.

## Key numbers

| Metric | Value |
|---|---|
| Live fast-payment systems worldwide | 100+ jurisdictions (ECB: 117, mid-2025) |
| Pix scale | ~63.4bn transactions (2024) |
| MED recovery | **7% of disputed value** (BCB official, 2025); ~89% of requests denied |
| MED 2.0 | Mandatory Feb 2, 2026 — traces up to **5 account layers** |
| Bre-B | Live 2025 · 200+ institutions · ~76m keys · **no recovery mechanism** |
| UK mandatory reimbursement | 88% / £173m repaid in year one — socializes loss, doesn't recover funds |

*Design implications built into Reversa: rail-agnostic by construction (same agents, thin country config — demoed on both Pix and Bre-B), multi-hop tracing as a first-class capability, a compounding cross-case mule-intelligence moat, and autonomy with regulator-grade auditability.*
