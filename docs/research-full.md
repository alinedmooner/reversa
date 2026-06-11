# The Research Behind Reversa
### Full investigation: instant payments, the fraud playbook, and the recovery gap

> Reversa did not start from a technology looking for a problem. It started from a domain investigation into instant-payment fraud in Latin America. This document preserves that investigation in full: the global context, the anatomy of the crime, Brazil's official recovery mechanism and why it underperforms, Colombia's regulatory greenfield, the category insight that defines the product — and, in **Appendix A**, a comparative reference of 100+ instant payment systems worldwide. A condensed version lives in **[research.md](research.md)**. Figures come from public sources (central bank publications, BIS, ECB, ACI Worldwide and reputable financial press); everything in the Reversa demo itself is synthetic.

---

## 1. The global wave: money became instant — and final

Instant payment rails are the fastest-adopted financial infrastructure of the past decade. Brazil's **Pix** (Banco Central do Brasil, 2020) became the country's dominant payment method within a few years, handling billions of transactions per month across virtually the entire banked population. India's **UPI** processes billions of monthly transactions. The US launched **FedNow**; Europe runs SEPA Instant; **more than 100 jurisdictions** — the ECB counts **117 live fast payment systems** as of mid-2025 — now operate or are building real-time rails. **ISO 20022** has emerged as the lingua franca of this generation of payment systems: a shared message vocabulary (`pacs`, `camt` families) that makes rails structurally similar even across borders.

In 2025, Colombia joined the wave with **Bre-B**, operated by Banco de la República: instant transfers, 24/7, addressed by simple keys ("llaves" — phone numbers, document IDs, emails, alphanumeric codes), interconnecting **more than two hundred financial institutions**, from incumbent banks to digital wallets, with ~76 million keys registered in its first months.

Two properties define these rails — and define the fraud problem:

1. **Speed**: settlement in seconds, around the clock.
2. **Irrevocability**: once settled, the transfer is final. There is no chargeback infrastructure.

For legitimate commerce these are features. For fraud, they are an attack surface.

## 2. Anatomy of instant-rail fraud

The dominant crime on instant rails is not card cloning or account takeover — it is **authorized-push-payment (APP) fraud**: the *legitimate account holder* is manipulated or coerced into sending an instant, irreversible transfer. This is why prevention models structurally underperform here: from the bank's perspective, the customer authorized the payment.

Brazil's Pix era produced a rich taxonomy of these scams ("golpes"): phishing and fake-support calls, relative-impersonation ("golpe do falso parente"), fake invoices and QR swaps, and — most notoriously — the **"sequestro relâmpago"** (express kidnapping), where victims are physically coerced into draining their accounts via Pix in minutes. Colombia inherits the same playbook for Bre-B, localized to its own social-engineering patterns.

After the transfer, the stolen money runs a well-rehearsed routine:

- **Layering**: the funds hop through a chain of **mule accounts** — recruited, rented, or stolen accounts spread across multiple institutions — typically two to five hops, each hop legally distancing the money from the crime.
- **Cashout**: the funds exit the system, most commonly to crypto (USDT) via OTC desks or P2P, or as physical cash.

The critical fact: **this entire routine takes minutes**. The race between the victim's report and the cashout is the whole game.

## 3. Brazil's answer: the MED — and why it recovers 7%

Brazil's central bank built the official response: the **MED (Mecanismo Especial de Devolução)**, launched in **November 2021**. The MED standardizes recovery: a victim reports the fraud to their institution; the institution files a MED request; the receiving institution can freeze the suspect balance; an analysis window of several **days** follows; if the claim is upheld, funds are returned.

The result is the single most important number in this project: **the MED recovers only ~7–14% of stolen amounts, depending on period and methodology — the BCB's official 2025 figure is 7% of disputed value, with roughly 89% of refund requests denied** (by the time the request lands, the money is already gone or the account is closed). Against an estimated **R$6.5 billion** in Pix fraud losses in 2025, that is the measured cost of human latency. The mechanism is not badly designed; it is **human-paced**. By the time an analyst reviews the case, the money has already layered through mules and left the system. The window in which the money is still *inside* the system — parked in some intermediate account, technically freezable — lasts minutes; the institutional response is measured in days.

Brazil knows this. **MED 2.0** — mandatory for participants since **February 2, 2026** (enforcement grace period to May 10, 2026) — extends tracing across up to **five layers** of accounts, allows blocking funds in **intermediate accounts** (not just the first destination), and puts the resolution on an 11-day clock. This is an explicit institutional acknowledgment of the two design truths Reversa is built on: recovery is a *multi-hop tracing* problem, and it is a *speed* problem. What MED 2.0 does not change is the actor: the loop is still triggered, reviewed, and executed at human speed.

## 4. Colombia: a rail without a safety net

Bre-B launched with **no MED equivalent**. There is no standardized, rail-level recovery mechanism: a defrauded victim depends on their bank's customer service line and ordinary complaint channels, under the general oversight of the **Superintendencia Financiera (SFC)** — which supervises conduct but cannot order refunds. Each institution improvises its own process; there is no cross-institution tracing, no standardized freeze request, no clock. Disputes move at help-desk speed against a crime that moves at network speed.

This is the strategic asymmetry between the two pilot markets:

| | **Brazil / Pix** | **Colombia / Bre-B** |
|---|---|---|
| Recovery mechanism | MED (since 2021), MED 2.0 (2026) | **None** |
| Measured recovery | ~7–14% (official 2025: **7% of disputed value**) | No standardized measurement |
| What Reversa is there | *The upgrade*: beat a mechanism that exists and underperforms | *The first mechanism*: greenfield |

## 5. The category insight: recovery, not prevention

The fraud-tech industry overwhelmingly sells **prevention** — scoring, friction, blocking before the money leaves. Prevention is a crowded category, and it is structurally incomplete: APP fraud defeats models because the rightful owner authorizes the payment under manipulation or duress.

Almost nobody competes in **recovery** — what happens to the money prevention misses. Today that money is written off as lost. The research says it isn't lost; it is **just faster than the humans chasing it**. The MED's measured ~7% is not a ceiling on what is recoverable. It is a measurement of **human latency**.

(The UK's mandatory APP-fraud reimbursement — the strongest victim-protection model in the world, with 88% of losses repaid in its first year — confirms the gap from the other side: reimbursement **socializes the loss**; it does not **recover the money**. The funds still end up with the criminals; the cost is redistributed to the financial system.)

That reframe defines the product category Reversa occupies: an empty, ownable space adjacent to (not competing with) every prevention vendor a bank already has.

## 6. Why autonomous agents — and why now

Recovery decomposes into exactly the loop agentic systems are built for:

1. **Understand** an unstructured, emotional victim report → structured case (intake);
2. **Investigate** by following money across a graph of accounts, enriched by institutional memory of known mules (tracing);
3. **Act** inside the live window by issuing the standardized recall — in ISO 20022 terms, a **camt.056** *FIToFIPaymentCancellationRequest* with reason code **FRAD**, answered by the receiving institution's **camt.029** *ResolutionOfInvestigation*, and settled, if accepted, by a **pacs.004** *PaymentReturn*;
4. **Document** the case in an auditable, regulator-ready dossier (evidence).

Every step is standardized, machine-readable, and latency-bound. The only missing piece was an actor fast enough to run the loop inside the window — and disciplined enough to document it for a regulator. Multi-agent systems are the first technology that can credibly be both.

## 7. Implications that shaped Reversa's design

- **Rail-agnostic by construction**: Pix and Bre-B differ in keys, currency, language, and regulator — but share the ISO 20022 skeleton and the mule playbook. Reversa's pipeline is identical across rails; only a thin country configuration changes (key formats, currency, regulatory context). The demo runs both a Brazilian Pix case and a Colombian Bre-B case through the same agents.
- **Multi-hop tracing as a first-class capability**: MED 2.0's five-layer mandate confirms the design — Reversa traces hop-by-hop and targets the *intermediate* account where funds are parked.
- **A compounding intelligence moat**: mule accounts recur across cases and victims. Persisting them (Agent Platform Memory Bank) means every solved case makes the next one faster — a network effect regulators and banks cannot easily replicate per-institution.
- **Autonomy with auditability**: speed wins the race; the grounded, citation-backed dossier wins the regulator. Both are non-negotiable in the design.

*Synthetic-data note: all accounts, institutions ("Banco Andes", "PagoYa" and their Brazilian counterparts), keys, and transactions in the Reversa demo are fictional. The research above informed the system's design; none of its real-world data flows into the demo.*

---

# Appendix A — Global Landscape of Instant / Real-Time Payment Systems (Comparative Reference)

*All figures are the most recent publicly available (2025–2026) from central banks (BCB, Banco de la República, ECB, BIS), the World Bank, ACI Worldwide and reputable financial press. Payment systems are referenced by name as factual, nominative use; no affiliation is implied.*

## A.1 Summary

- **Over 100 jurisdictions** now run live instant/fast payment systems — the ECB counts **117 distinct FPS globally** with 523 cross-border connections as of June 2025. Brazil's Pix (~63.4bn transactions in 2024) and India's UPI (228.3bn in 2025) are the global leaders; Colombia's Bre-B (live Sept–Oct 2025) is the newest major Latin American rail.
- The **recovery gap is real and central to Reversa's thesis**: Brazil's Pix MED recovered only **7% of disputed fraud value in 2025** (BCB), prompting mandatory MED 2.0 (5-layer tracing, Feb 2026); Colombia's Bre-B has **no MED-equivalent fund-recovery mechanism at all**; the UK runs the world's strongest *reimbursement* model (mandatory 50/50 liability split up to £85,000 since Oct 2024 — **88% / £173m reimbursed in year one**); most other systems sit between "prevention only" and "voluntary return."
- Instant payment design has converged globally on **alias/key-based addressing, QR codes, 24/7 availability, near-instant irrevocable settlement, and ISO 20022 messaging** — precisely the features that make social-engineering fraud lucrative and post-hoc recovery hard.

## A.2 Key findings

1. **Irrevocability is the universal design feature that creates the fraud-recovery problem.** Across Pix, Bre-B, UPI, FedNow, RTP, SEPA Instant and others, completed transfers are final/credit-push with no clawback. The entire fraud burden shifts to either prevention (verification of payee, name display) or post-hoc recovery — and the latter is weak or absent in most countries.
2. **Brazil is the global frontier on fraud recovery — not because the MED works well, but because it is being forced to evolve.** The BCB reported only 7% of disputed Pix value recovered in 2025; industry analysis found ~89% of MED refund requests denied (funds already gone or accounts closed). Against R$6.5 billion in 2025 Pix fraud losses, MED 2.0 (mandatory Feb 2, 2026; grace to May 10, 2026) introduces multi-hop tracing across up to 5 account layers, automatic preventive blocks, and an 11-day resolution window.
3. **Colombia's Bre-B is the clearest example of the recovery gap** — a Pix-inspired, central-bank-operated rail with NO fund-recovery mechanism comparable to the MED. This is exactly the whitespace Reversa targets.
4. **Only the UK has shifted liability decisively to PSPs** via mandatory APP-fraud reimbursement (Oct 2024); the EU is moving toward prevention-by-mandate (Verification of Payee, Oct 2025). Note the category distinction: reimbursement *socializes the loss*; it does not *recover the money*.

## A.3 Global scale and sources

The BIS and the ECB both report **over 100 jurisdictions** with live fast payment systems as of 2024–2025; the ECB's June 2025 analysis counts **117 FPS with 523 dyadic cross-border connections**. ACI Worldwide's *Prime Time for Real-Time* tracks 51 real-time markets and reported **266.2 billion** real-time transactions globally in 2023 (+42.2% YoY), forecasting 575 billion by 2028, with India accounting for roughly half the global total. BIS CPMI commentary (April 2026) ranks Brazil first in fast-payment use in 2024 at **298 payments per capita**, followed by Korea (189) and Argentina (149). The World Bank's Fast Payments Toolkit and BIS confirm public-sector-led systems achieve the highest adoption.

## A.4 Latin America (Reversa's home region)

| Country | System | Operator | Launch | Scale (latest) | Key features | Fraud/recovery status | ISO 20022 |
|---|---|---|---|---|---|---|---|
| **Brazil** | **Pix** | Central Bank of Brazil (BCB) | Nov 2020 | ~63.4bn txns (2024), ~$4.6tn value; world's highest fast-payment use at 298 payments per capita (2024, BIS); single-day record 276.7m (Jun 2025) | Keys ("chaves": CPF/CNPJ/phone/email/random EVP), static/dynamic QR, 24/7, contactless (Feb 2025), Pix Automático (Jun 2025) | **MED** since Nov 2021; recovered only **7% of disputed value in 2025** (BCB); ~89% of requests denied; **MED 2.0 mandatory Feb 2, 2026** — multi-hop tracing up to 5 layers, automatic preventive blocks, 11-day resolution; enforcement grace to May 10, 2026 | Yes |
| **Colombia** | **Bre-B** | Banco de la República (central bank) | Keys Jul 2025; live Sep 23 / full Oct 6, 2025 | ~76m+ keys registered, ~33m users by late 2025; ~3.6m txns/day avg Dec 2025; **200+ participating institutions** via interoperable nodes | Alias-based ("llaves": cédula/phone/email/alphanumeric), interoperable nodes (Transfiya, Entrecuentas, Visionamos), 24/7, <20s settlement, free for individuals to at least 2029 | **No MED-equivalent recovery mechanism.** Transfers irrevocable/final; recovery depends on voluntary return by the recipient or civil/criminal action. SFC supervises but cannot order refunds; industry bodies warn of a Brazil-style fraud surge | Aligned |
| Colombia (predecessors) | Transfiya / PSE | ACH Colombia / private | Transfiya 2019; PSE earlier | Transfiya now a Bre-B node; PSE remains dominant for online A2A | Transfiya: phone alias, 24/7, capped; PSE: bank-redirect online payments | Limited; being absorbed into Bre-B | Partial |
| **Mexico** | SPEI + CoDi / DiMo | Banco de México | SPEI 2004 (24/7 since 2015); CoDi 2019; DiMo 2023 | SPEI >6bn operations in 2025; CoDi adoption weak; DiMo grew 5.6m→12.2m users in 2024 | SPEI: CLABE-based RTGS; CoDi: QR/NFC; DiMo: phone-alias overlay; "SPEI 2.0" homologation proposed (2026) | No central recovery mechanism; prevention-focused | Proprietary; modernizing |
| **Peru** | Yape / Plin (+ CCE) | BCP (Yape), bank consortium (Plin); BCRP-mandated interoperability | Yape 2016; Plin 2020; interop Apr 2023 | Yape ~14m+ active users (2025) | Phone-alias and QR; interoperable since 2023; caps raised 2026 | No formal recovery mechanism; wallet-extortion is a major problem — a Nov 2025 bill proposes opt-in accept/reject transfers | Wallet-based |
| **Argentina** | Transferencias 3.0 / MODO | BCRA; bank consortium (MODO) | 2021; MODO 2020 | 149 fast payments per capita (2024, BIS) | Interoperable QR, alias-based (CVU/CBU), 24/7 | Prevention-focused; no MED-equivalent | Aligned |
| **Costa Rica** | SINPE Móvil | Central Bank (BCCR) | 2015 | >80% of population 15+ are active users (2025) | Phone-number alias, 24/7, free/low-cost | Prevention-focused; no MED-equivalent | SINPE core |
| **Chile** | TEF / Transferencias en Línea | Bank consortium | 2008 | Widely used A2A | Account-based online transfers | Prevention-focused | Modernizing |
| **Uruguay** | Toke / ACH Transferencias Inmediatas | Central bank / ACH | Toke Sep 2024 | First adopter of the Pix model abroad | QR-based | Early stage | Aligned |

## A.5 Asia-Pacific

| Country | System | Operator | Launch | Scale (latest) | Key features | Fraud/recovery status | ISO 20022 |
|---|---|---|---|---|---|---|---|
| **India** | **UPI** (on IMPS) | NPCI (RBI-regulated) | 2016 | **228.3bn txns in 2025 (+29% YoY)**; Dec 2025 record 21.63bn/month; ~half of global real-time volume | VPA alias, QR, 24/7, UPI Lite, cross-border (8 countries) | No mandatory reimbursement; prevention via beneficiary-name display (Jun 2025), AI mule-detection; ~1.3m fraud cases FY24-25 | Aligned |
| Thailand | PromptPay | Bank of Thailand / NITMX | 2016/17 | >90m registrations; ~74m txns/day | Phone/ID alias, QR, cross-border QR links | Prevention-focused | Yes |
| Singapore | PayNow (on FAST) | ABS/BCS; MAS oversight | 2017 | Near-universal; cross-border hub (Project Nexus) | Phone/NRIC/UEN alias, QR, 24/7 | Shared-responsibility scam framework; prevention-focused | Yes |
| Malaysia | DuitNow (on RPP) | PayNet; BNM | 2018 | Leads SEA e-commerce A2A | Phone/NRIC alias, QR, 24/7 | Prevention-focused | Yes |
| Indonesia | BI-FAST (+ QRIS) | Bank Indonesia | Dec 2021 | ~55% consumer RTP usage; high growth | Proxy addresses, QR, real-time fraud detection | Prevention-focused | Yes |
| Philippines | InstaPay (+ PESONet) | BancNet; BSP | 2018 | Rapid growth; per-txn caps | Credit-push, QR, <20s, 24/7 | Prevention-focused | Adopting |
| China | IBPS | PBoC / CNCC | 2010 | >18bn txns (2021); 2nd to India | Phone identifiers, QR/NFC, 24/7 | Prevention-focused | Yes |
| Japan | Zengin System | Zengin-Net (JBA) | 1973 (24/7 since 2018) | Nationwide coverage | Account-based; opening to wallets | Prevention-focused | Migrating |
| South Korea | EBS | KFTC | 2001 | 189 fast payments per capita (2024, BIS) | Account/mobile-based, 24/7 | Prevention-focused | Aligned |
| Australia | NPP (Osko, PayID, PayTo) | AP+; RBA oversight | Feb 2018 | ~2bn txns in 2025; >25m PayIDs | PayID alias, Confirmation of Payee, PayTo | Prevention-focused; no reimbursement mandate | Yes |

## A.6 Europe

| Country/region | System | Operator | Launch | Scale (latest) | Key features | Fraud/recovery status | ISO 20022 |
|---|---|---|---|---|---|---|---|
| **Eurozone/EEA** | **SEPA Instant (SCT Inst)** on TIPS/RT1 | EPC scheme; ECB (TIPS), EBA Clearing (RT1) | 2017; IPR mandate 2024–25 | ~89% of eurozone PSPs joined; ~23% of credit transfers (2024) | IBAN-based, 24/7, ≤10s | **Verification of Payee mandatory Oct 9, 2025**; no EU-wide reimbursement mandate | Yes |
| **UK** | **Faster Payments** (+ CHAPS) | Pay.UK; PSR/BoE | 2008 | Dominant UK A2A rail | Confirmation of Payee, 24/7 | **Mandatory APP-fraud reimbursement since Oct 7, 2024**: up to £85,000, 5-day refund, cost split 50/50 sending/receiving PSP; **88% (£173m) of losses reimbursed in year one** vs 65% under the prior voluntary code | Migrating |
| Sweden | Swish (on RIX-INST) | Bank consortium; Riksbank | 2012 | ~8–8.9m users (≈⅔ of population) | Phone-alias, QR, 24/7 | Prevention-focused | Aligned |
| Spain | Bizum | Bank consortium (on SCT Inst) | 2016 | Top-10 global RTP brand | Phone/email alias, P2P + P2B | Prevention + EU VoP | Yes |
| Poland | BLIK (on Express Elixir) | Polski Standard Płatności | 2015 | >20m users (Dec 2025) | One-time codes, QR, P2P | Prevention-focused | Aligned |
| Hungary | AFR (+ Qvik) | MNB | 2020 (mandatory) | Qvik at >31,000 merchants (Q2 2025) | QR/NFC/request-to-pay | Prevention-focused | Yes |
| Nordics | MobilePay / Vipps | Vipps MobilePay | 2013 | Dominant Nordic wallets | Phone-alias, 24/7 | Prevention-focused | Aligned |

## A.7 North America

| Country | System | Operator | Launch | Scale (latest) | Key features | Fraud/recovery status | ISO 20022 |
|---|---|---|---|---|---|---|---|
| USA | RTP | The Clearing House | 2017 | $246bn / 343m txns (2024); Q2 2025 $481bn; limit $10m (Feb 2025) | Credit-push, request-for-payment, 24/7, no clawback | Prevention only; no reimbursement mandate | Yes (native) |
| USA | FedNow | Federal Reserve | Jul 2023 | ~$853bn in 2025 (est.); >1,500 FIs; limit to $10m (Nov 2025) | Credit-push, 24/7, negative-list fraud controls | Prevention only; no reimbursement mandate | Yes (native) |
| Canada | Interac e-Transfer (live); Real-Time Rail (delayed) | Interac; Payments Canada | e-Transfer live; RTR delayed | e-Transfer widely used | Email/phone alias | Prevention-focused | RTR: yes |

## A.8 Africa & Middle East

| Country | System | Operator | Launch | Scale (latest) | Key features | Fraud/recovery status | ISO 20022 |
|---|---|---|---|---|---|---|---|
| **Nigeria** | NIP → National Payment Stack | NIBSS; CBN | NIP 2011; NPS Nov 2025 | >9bn txns/yr; first African IPS rated "Mature" (SIIPS 2025) | Account/alias, 24/7 | **Industry dispute-resolution platform** (CBN-driven) — notable for emerging markets | Migrating |
| South Africa | PayShap | BankservAfrica; SARB | Mar 2023 | >30m txns since launch | ShapID alias, Request-to-Pay | Prevention-focused | Yes |
| Regional | PAPSS (Africa), BUNA/AFAQ (Arab), Transfer365 (C. America) | Various | Various | Cross-border rails | Multi-currency instant settlement | Varies | Yes |

## A.9 Fraud RECOVERY mechanisms — the core differentiator

| System | Recovery model | Effectiveness / status | Liability |
|---|---|---|---|
| **Brazil — Pix MED / MED 2.0** | Regulator-operated Special Return Mechanism; MED 2.0 adds multi-hop tracing (up to 5 layers) and automatic preventive blocks | Original MED recovered only **7% of disputed value in 2025** (BCB); ~89% of requests denied; MED 2.0 mandatory Feb 2026, 11-day window | Shared via tracing; recipient's balance must still exist |
| **Colombia — Bre-B** | **None.** No MED-equivalent | No central recovery; transfers irrevocable; SFC cannot order refunds | Falls on the victim; recipient must agree to return |
| **UK — Faster Payments** | **Mandatory reimbursement** of APP-fraud victims | In force Oct 2024; up to £85,000; **88% (£173m) reimbursed in year one** | 50/50 sending/receiving PSP — strongest liability shift globally |
| **EU — SEPA Instant** | Prevention-first: Verification of Payee mandatory Oct 2025 | Reduces misdirection fraud; recovery not guaranteed | On PSPs to provide VoP |
| **India — UPI** | Prevention + grievance redressal | Name display, AI mule detection; high fraud volume | Largely on the user |
| **USA — RTP / FedNow** | Prevention only; no clawback | Network-level controls | On the sender |
| **Australia — NPP** | Prevention (CoP, PayID) | No reimbursement mandate | On the user |
| **Nigeria — NIP/NPS** | Industry dispute-resolution platform | Credited with reducing disputes | Shared via platform |

## A.10 What this landscape means for Reversa

1. **The recovery gap is global whitespace.** Only the UK has a true liability-shift model — and reimbursement *socializes the loss*; it does not *recover the money*. Brazil is the only major system building automated multi-hop fund tracing. Everyone else — including every LATAM rail — sits between "prevention only" and "voluntary return." Reversa occupies the empty category: autonomous recovery of the funds themselves.
2. **MED 2.0 is the regulatory blueprint that validates the design.** Five-layer tracing, preventive blocks on intermediate accounts, a clock on resolution — that is precisely Reversa's pipeline, with one difference: MED 2.0 still runs at institutional speed, and the original MED's 7% recovery rate is the measured cost of that latency. Reversa benchmarks itself against MED 2.0's tracing depth, executed at machine speed.
3. **Market thesis as built into this project: Colombia-first, Brazil-portable, rail-agnostic by design.** Colombia/Bre-B is the clearest greenfield in the world — a Pix-class rail, 200+ institutions, zero recovery mechanism — where Reversa is not an upgrade but *the first mechanism that exists*. Brazil is the expansion market with a regulatory tailwind: the MED 2.0 enforcement window (Feb–May 2026) creates immediate demand for tracing-and-recovery tooling across institutions still adapting. The demo therefore runs the same agents on both rails — a Pix case (judge-familiar, MED-verifiable) and a Bre-B case (the greenfield) — swapping only a thin country configuration. Peru (extortion-driven legislative momentum) and Mexico (SPEI 2.0 roadmap) are natural follow-ons.
4. **Honest benchmarks that would change the picture:** (a) Banco de la República announcing a MED-style mechanism would narrow the Colombian greenfield — while simultaneously validating the category; (b) MED 2.0 recovery rates materially above the ~7% baseline after full rollout would shift the Brazil pitch from replacement to augmentation-at-speed; (c) UK-style mandatory reimbursement spreading to more markets would move the buyer to the bank's loss-mitigation function — strengthening, not weakening, the case for recovery tooling.

## A.11 Caveats

- Fraud-loss and recovery figures vary by source and methodology; Brazil's MED recovery rate is reported variously between ~7% and ~15% depending on period and whether measured by value or case count. The BCB's official 2025 figure is **7% of disputed value**, with ~89% of requests denied.
- Forward-looking claims (e.g., projected MED 2.0 impact, Colombian fraud-surge warnings) are projections, flagged as such.
- Scale metrics for wallet-based systems mix registered vs. active users; treat as order-of-magnitude.
- "ISO 20022 status" is simplified: several systems run proprietary or hybrid messaging while migrating.
- Bre-B figures cover its first months of operation and are growing rapidly. The "no recovery mechanism" finding rests on Banco de la República's own regulatory framing, the absence of any return mechanism in its dispute rules, and bank-level terms that make recovery contingent on voluntary return by the recipient.
